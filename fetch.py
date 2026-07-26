"""Utilities for fetching and rendering web pages with Selenium."""

from __future__ import annotations

import logging
from typing import Optional

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


def fetch_html(url: str) -> str:
    """Render a page in headless Chrome and return the final HTML.

    Args:
        url: The target URL to open.

    Returns:
        The rendered HTML as a string.

    Raises:
        ValueError: If the URL is empty or invalid.
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("A valid URL is required.")

    normalized_url = url.strip()
    if not normalized_url.startswith(("http://", "https://")):
        raise ValueError("The URL must start with http:// or https://")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver: Optional[webdriver.Chrome] = None
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )
        driver.get(normalized_url)

        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.body && document.body.innerHTML.length > 0")
        )

        return driver.page_source
    except (TimeoutException, WebDriverException) as exc:
        logger.exception("Failed to render %s", normalized_url)
        return ""
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.exception("Unexpected error while fetching %s", normalized_url)
        return ""
    finally:
        if driver is not None:
            driver.quit()
