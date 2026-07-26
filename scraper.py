"""Utilities to extract common product details from HTML content."""

from __future__ import annotations

import re
from typing import Optional

from bs4 import BeautifulSoup


def _clean_text(text: Optional[str]) -> Optional[str]:
    if text is None:
        return None
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned or None


def _extract_title(soup: BeautifulSoup) -> Optional[str]:
    for selector in ["meta[property='og:title']", "meta[name='twitter:title']", "title"]:
        element = soup.select_one(selector)
        if element and element.get("content"):
            return _clean_text(element.get("content"))
        if element and element.get_text(strip=True):
            return _clean_text(element.get_text(strip=True))

    for tag in soup.find_all(["h1", "h2"], limit=5):
        text = _clean_text(tag.get_text(" ", strip=True))
        if text:
            return text
    return None


def _extract_price(soup: BeautifulSoup) -> Optional[str]:
    for attr in ["content", "value"]:
        for selector in [
            "meta[itemprop='price']",
            "meta[property='product:price:amount']",
            "meta[name='price']",
        ]:
            element = soup.select_one(selector)
            if element and element.get(attr):
                return _clean_text(element.get(attr))

    for tag in soup.find_all(True):
        text = _clean_text(tag.get_text(" ", strip=True))
        if not text:
            continue
        if re.search(r"(?:\$|€|£)\s?\d+(?:[.,]\d{2})?", text):
            return text
    return None


def _extract_rating(soup: BeautifulSoup) -> Optional[str]:
    for selector in [
        "meta[itemprop='ratingValue']",
        "meta[name='rating']",
        "[itemprop='ratingValue']",
    ]:
        element = soup.select_one(selector)
        if element:
            value = element.get("content") or element.get_text(strip=True)
            if value:
                return _clean_text(value)

    for tag in soup.find_all(True):
        text = _clean_text(tag.get_text(" ", strip=True))
        if not text:
            continue
        match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*5", text)
        if match:
            return match.group(1)
    return None


def _extract_reviews(soup: BeautifulSoup) -> Optional[str]:
    for selector in [
        "meta[itemprop='reviewCount']",
        "meta[name='reviews']",
        "[itemprop='reviewCount']",
    ]:
        element = soup.select_one(selector)
        if element:
            value = element.get("content") or element.get_text(strip=True)
            if value:
                return _clean_text(value)

    for tag in soup.find_all(True):
        text = _clean_text(tag.get_text(" ", strip=True))
        if not text:
            continue
        match = re.search(r"(\d+)\s+(?:reviews?|ratings?)", text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def _extract_image(soup: BeautifulSoup) -> Optional[str]:
    for selector in ["meta[property='og:image']", "meta[name='twitter:image']"]:
        element = soup.select_one(selector)
        if element and element.get("content"):
            return _clean_text(element.get("content"))

    image_tag = soup.find("img")
    if image_tag and image_tag.get("src"):
        return _clean_text(image_tag.get("src"))
    return None


def _extract_availability(soup: BeautifulSoup) -> Optional[str]:
    for selector in ["meta[itemprop='availability']", "[class*='availability']", "[id*='availability']"]:
        element = soup.select_one(selector)
        if element:
            value = element.get("content") or element.get_text(strip=True)
            if value:
                return _clean_text(value)
    return None


def _extract_delivery(soup: BeautifulSoup) -> Optional[str]:
    for tag in soup.find_all(True):
        text = _clean_text(tag.get_text(" ", strip=True))
        if not text:
            continue
        if re.search(r"delivery|shipping|free shipping|free delivery", text, re.IGNORECASE):
            return text
    return None


def extract_details(html: str) -> dict[str, Optional[str]]:
    """Extract common product data from an HTML page string.

    The extraction uses generic heuristics so it can work across many product pages.

    Args:
        html: The rendered HTML content for a page.

    Returns:
        A dictionary containing the available product details.
    """
    if not isinstance(html, str) or not html.strip():
        return {
            "title": None,
            "price": None,
            "rating": None,
            "reviews": None,
            "image": None,
            "availability": None,
            "delivery": None,
        }

    soup = BeautifulSoup(html, "html.parser")
    return {
        "title": _extract_title(soup),
        "price": _extract_price(soup),
        "rating": _extract_rating(soup),
        "reviews": _extract_reviews(soup),
        "image": _extract_image(soup),
        "availability": _extract_availability(soup),
        "delivery": _extract_delivery(soup),
    }
