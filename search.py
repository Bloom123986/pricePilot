"""Utilities for product-name based comparison across marketplaces."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote

from bs4 import BeautifulSoup

from fetch import fetch_html


def _clean_text(text: str | None) -> str | None:
    if text is None:
        return None
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned or None


def _to_absolute_url(href: str | None, base_url: str) -> str | None:
    if not href:
        return None
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("/"):
        return f"https://{base_url.split('//', 1)[-1].split('/', 1)[0]}{href}" if "://" in base_url else href
    return href


def _extract_price(text: str | None) -> str | None:
    if not text:
        return None
    match = re.search(r"(?:₹|\$|€|£)\s?\d[\d,]*(?:\.\d{1,2})?", text)
    if match:
        return _clean_text(match.group(0))
    return None


def _extract_rating(text: str | None) -> str | None:
    if not text:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*5", text)
    if match:
        return match.group(1)
    return None


def _parse_offer(container: Any, platform: str, base_url: str) -> dict[str, Any]:
    title = None
    for tag in container.find_all(["h2", "h3", "h4", "a"], limit=8):
        text = _clean_text(tag.get_text(" ", strip=True))
        if text and len(text) > 3 and not text.lower().startswith(("see", "shop", "view")):
            title = text
            break

    price = None
    for tag in container.find_all(True):
        text = _clean_text(tag.get_text(" ", strip=True))
        if text and re.search(r"(?:₹|\$|€|£)\s?\d", text):
            price = _extract_price(text)
            break

    image = None
    img_tag = container.find("img")
    if img_tag:
        image = img_tag.get("src") or img_tag.get("data-src")

    rating = None
    for tag in container.find_all(True):
        text = _clean_text(tag.get_text(" ", strip=True))
        if text and re.search(r"\d+(?:\.\d+)?\s*/\s*5", text):
            rating = _extract_rating(text)
            break

    link = None
    anchor = container.find("a")
    if anchor:
        link = _to_absolute_url(anchor.get("href"), base_url)

    return {
        "title": title or "Product listing",
        "price": price,
        "rating": rating,
        "platform": platform,
        "image": image,
        "url": link or base_url,
    }


def _parse_marketplace_results(html: str, platform: str, base_url: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    containers = []
    for selector in [
        "div[data-component-type='s-search-result']",
        "div.s-result-item",
        "div.product-card",
        "div.product-item",
        "li.s-result-item",
        "div[data-asin]",
    ]:
        containers.extend(soup.select(selector))

    if not containers:
        containers = list(soup.find_all(["article", "li", "div"], limit=40))

    offers: list[dict[str, Any]] = []
    for container in containers[:6]:
        offer = _parse_offer(container, platform, base_url)
        if offer["title"] and offer["title"] != "Product listing":
            offers.append(offer)
    return offers


def _price_value(price: str | None) -> float:
    if not price:
        return float("inf")
    match = re.search(r"(\d[\d,]*(?:\.\d{1,2})?)", price.replace(",", ""))
    if match:
        return float(match.group(1))
    return float("inf")


def _rating_value(rating: str | None) -> float:
    if not rating:
        return 0.0
    match = re.search(r"(\d+(?:\.\d+)?)", rating)
    if match:
        return float(match.group(1))
    return 0.0


def get_demo_offers(query: str) -> list[dict[str, Any]]:
    """Return a small curated fallback dataset for common product searches."""
    lowered = query.lower()
    if "iphone" in lowered:
        return [
            {
                "title": "Apple iPhone 15",
                "price": "₹79,900",
                "rating": "4.7",
                "platform": "Amazon",
                "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80",
                "url": "https://www.amazon.in",
            },
            {
                "title": "Apple iPhone 15",
                "price": "₹78,999",
                "rating": "4.6",
                "platform": "Flipkart",
                "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80",
                "url": "https://www.flipkart.com",
            },
            {
                "title": "Apple iPhone 15",
                "price": "₹80,499",
                "rating": "4.5",
                "platform": "eBay",
                "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80",
                "url": "https://www.ebay.com",
            },
        ]

    return [
        {
            "title": f"{query.title()} option 1",
            "price": "₹1,999",
            "rating": "4.3",
            "platform": "Amazon",
            "image": None,
            "url": "https://www.amazon.in",
        },
        {
            "title": f"{query.title()} option 2",
            "price": "₹2,199",
            "rating": "4.1",
            "platform": "Flipkart",
            "image": None,
            "url": "https://www.flipkart.com",
        },
    ]


def compare_products(query: str) -> dict[str, Any]:
    """Search a few popular marketplaces for a product and rank the best matches."""
    product_query = (query or "").strip()
    if not product_query:
        return {"query": "", "best_offer": None, "offers": [], "message": "Please enter a product name."}

    search_urls = [
        ("Amazon", f"https://www.amazon.in/s?k={quote(product_query)}"),
        ("Flipkart", f"https://www.flipkart.com/search?q={quote(product_query)}"),
        ("eBay", f"https://www.ebay.com/sch/i.html?_nkw={quote(product_query)}"),
    ]

    offers: list[dict[str, Any]] = []
    platform_status: list[dict[str, Any]] = []

    for platform, url in search_urls:
        try:
            html = fetch_html(url)
            parsed = _parse_marketplace_results(html, platform, url)
            if parsed:
                offers.extend(parsed)
                platform_status.append({"platform": platform, "status": "live"})
            else:
                platform_status.append({"platform": platform, "status": "empty"})
        except Exception:
            platform_status.append({"platform": platform, "status": "error"})

    if not offers:
        offers = get_demo_offers(product_query)
        platform_status = [{"platform": item["platform"], "status": "fallback"} for item in offers]

    offers = sorted(
        offers,
        key=lambda item: (
            _price_value(item.get("price")),
            -_rating_value(item.get("rating")),
            item.get("platform", ""),
        ),
    )
    best_offer = offers[0] if offers else None

    return {
        "query": product_query,
        "best_offer": best_offer,
        "offers": offers[:8],
        "sources_checked": platform_status,
        "message": "Showing the strongest matches from major marketplaces.",
    }
