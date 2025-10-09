# app/skills/extractors/flipkart.py
import time
from typing import List, Dict, Optional
from urllib.parse import quote_plus
from app.utils.logger import logger
from app.browser.controller import BrowserController
from app.utils.money import parse_price_to_int


# ---------- Utility helpers ----------

def _dismiss_flipkart_login(bc: BrowserController) -> None:


    logger.info(f"[DEBUG] Entering {__name__} extractor. bc={bc}, page_valid={getattr(bc, 'page', None) is not None}")

    assert bc is not None and bc.page is not None, "BrowserController or page not initialized"
    """Close Flipkart login modal if it appears."""
    selectors = [
        "button._2KpZ6l._2doB4z",
        "button._2KpZ6l._2doB4z._3AWRsL",
        "button._2KpZ6l._2doB4z._1oVJPM",
        "img[alt='Close']",
        "button[aria-label='Close']",
        "._2KpZ6l._2doB4z",
    ]
    for sel in selectors:
        try:
            bc.page.locator(sel).first.click(timeout=1000)
            logger.info("✅ Closed Flipkart login/modal popup.")
            return
        except Exception:
            pass


def _parse_rating(value: Optional[str]) -> Optional[float]:
    try:
        return float(value) if value else None
    except Exception:
        return None


# ---------- Main extractor ----------

def extract_flipkart_products(
    bc: Optional[BrowserController],
    max_results: int,
    query: Optional[str] = None,
    max_price: Optional[int] = None,
) -> List[Dict]:
    assert bc is not None and bc.page is not None, "BrowserController or page not initialized"
    """Scrape product listings from Flipkart search results."""
    if bc is None:
        raise ValueError("Flipkart extractor requires a BrowserController instance.")

    results: List[Dict] = []
    q = quote_plus(query or "laptops under 50000")
    url = f"https://www.flipkart.com/search?q={q}"
    logger.info(f"🌐 Navigating Flipkart: {url}")

    # Load the page
    bc.goto(url, timeout=60000)
    _dismiss_flipkart_login(bc)
    bc.page.wait_for_load_state("domcontentloaded")

    # ---------- Attempt to find product anchors ----------
    anchor_selectors = [
        "a.CGtC98",                   # new Flipkart layout (2024+)
        "div.tUxRFH a.CGtC98",
        "a.IRpwTa",                   # legacy card
        "a._1fQZEK",                  # grid layout
        "div._1AtVbE a.s1Q9rs",       # alternate style
    ]

    items = []
    for sel in anchor_selectors:
        try:
            bc.page.wait_for_selector(sel, timeout=8000)
            items = bc.page.query_selector_all(sel)
            if items:
                logger.info(f"✅ Found {len(items)} product anchors using {sel}")
                break
        except Exception:
            continue

    # ---------- Handle lazy-loaded results ----------
    if not items:
        logger.info("🌀 Scrolling for lazy-loaded Flipkart results...")
        for _ in range(5):
            bc.page.mouse.wheel(0, 3000)
            time.sleep(1.0)
            items = bc.page.query_selector_all("a.CGtC98") or []
            if items:
                logger.info(f"✅ Found {len(items)} products after scroll.")
                break

    if not items:
        logger.warning("⚠️ No products found on Flipkart after all attempts.")
        return results

    parsed: List[Dict] = []
    for item in items[: max_results * 3]:  # over-fetch to allow filtering
        try:
            # --- Title ---
            title_el = (
                item.query_selector("div.KzDlHZ")
                or item.query_selector("div._4rR01T")
                or item.query_selector("a.s1Q9rs")
            )
            title = title_el.inner_text().strip() if title_el else None

            # --- Price ---
            price_el = (
                item.query_selector("div.Nx9bqj._4b5DiR")
                or item.query_selector("div._30jeq3._1_WHN1")
                or item.query_selector("div._30jeq3")
            )
            price_text = price_el.inner_text().strip() if price_el else ""
            price_int = parse_price_to_int(price_text)

            # --- Link & Image ---
            href = item.get_attribute("href")
            href = (
                f"https://www.flipkart.com{href}"
                if href and href.startswith("/")
                else href
            )
            image_el = item.query_selector("img")
            image = image_el.get_attribute("src") if image_el else None

            # --- Ratings ---
            rating_el = (
                item.query_selector("div._3LWZlK")
                or item.query_selector("span._1lRcqv")
                or item.query_selector("div.XQDdHH")
            )
            rating_text = rating_el.inner_text().strip() if rating_el else None
            formatted_rating = f"{rating_text} out of 5 stars" if rating_text else "N/A"

            # --- Skip invalid items ---
            if not title or not href:
                continue
            if max_price is not None and price_int is not None and price_int > max_price:
                continue

            parsed.append(
                {
                    "title": title,
                    "price": price_text or "N/A",
                    "price_value": price_int if price_int is not None else 99999999,
                    "rating": formatted_rating,
                    "image": image,
                    "link": href
                }
            )

        except Exception as e:
            logger.warning(f"⚠️ Flipkart item parse failed: {e}")

    # ---------- Sort and return ----------
    parsed.sort(key=lambda x: x.get("price_value", 10**9))
    final = parsed

    logger.info(f"🧮 Parsed {len(final)} Flipkart products successfully.")
    return final
