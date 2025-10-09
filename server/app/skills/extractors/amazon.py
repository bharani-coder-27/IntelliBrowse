# app/skills/extractors/amazon.py
from typing import List, Dict, Optional
from urllib.parse import quote_plus
from app.utils.logger import logger
from app.browser.controller import BrowserController
from app.utils.money import parse_price_to_int


def _norm_link(href: Optional[str]) -> Optional[str]:
    if not href:
        return None
    return href if href.startswith("http") else f"https://www.amazon.in{href}"


def extract_amazon_products(
    bc: Optional[BrowserController],
    max_results: int = 5,
    query: Optional[str] = None,
    max_price: Optional[int] = None,
) -> List[Dict]:
    
    logger.info(f"[DEBUG] Entering {__name__} extractor. bc={bc}, page_valid={getattr(bc, 'page', None) is not None}")
    assert bc is not None and bc.page is not None, "BrowserController or page not initialized"


    """
    Robust Amazon extractor based on verified DOM:
    - Cards: div.s-main-slot div[data-component-type="s-search-result"][data-asin]
    - Title/Link: h2 > a (fallback: any <a href*="/dp/">, then image alt)
    - Price: prefer a-price[data-a-color="base"] > .a-offscreen (fallbacks included)
    - Keeps items with missing price (sorted last)
    - Skips obvious non-products (plan/cover/warranty/gift card)
    """

    results: List[Dict] = []

    q = quote_plus(query or "laptops under 50000")
    url = f"https://www.amazon.in/s?k={q}"
    logger.info(f"Navigating Amazon: {url}")
    bc.goto(url, timeout=60_000)

    # Wait for the real faceouts
    try:
        bc.page.wait_for_selector("div.s-main-slot", timeout=15_000)
        bc.page.wait_for_selector(
            'div.s-main-slot div[data-component-type="s-search-result"][data-asin]:not([data-asin=""])',
            timeout=15_000,
        )
    except Exception:
        logger.warning("Amazon: No search-result faceouts found.")
        return results

    cards = bc.page.query_selector_all(
        'div.s-main-slot div[data-component-type="s-search-result"][data-asin]:not([data-asin=""])'
    )
    logger.info(f"Amazon: Found {len(cards)} search-result faceouts")

    parsed: List[Dict] = []
    for card in cards[: max_results * 4]:  # grab extras; we’ll filter and slice later
        try:
            # ----- Title + Link (robust) -----
            link_el = (
                card.query_selector(
                    "h2 a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal"
                )
                or card.query_selector("h2 a.a-link-normal")
                or card.query_selector("h2 a")
            )

            title_text = None
            href = None
            if link_el:
                span = link_el.query_selector("span")
                title_text = (span.inner_text().strip() if span else link_el.inner_text().strip()) or None
                href = _norm_link(link_el.get_attribute("href"))

            # Fallback: any product anchor with /dp/
            if not href:
                dp_link = card.query_selector('a[href*="/dp/"]')
                if dp_link:
                    href = _norm_link(dp_link.get_attribute("href"))
                    if not title_text:
                        maybe_title = (dp_link.inner_text() or "").strip()
                        title_text = maybe_title or title_text

            # Final fallback for title: image alt
            if not title_text:
                img = card.query_selector("img.s-image[alt]")
                if img:
                    title_text = img.get_attribute("alt")

            if not href or not title_text:
                # Not a standard product faceout; skip quietly
                continue

            # ----- Price (prefer selling price, avoid M.R.P) -----
            price_text = "N/A"
            price_el = (
                card.query_selector('span.a-price[data-a-color="base"] span.a-offscreen')
                or card.query_selector('span.a-price:not(.a-text-price) span.a-offscreen')
                or card.query_selector("span.a-price span.a-offscreen")
            )
            if price_el:
                candidate = price_el.inner_text().strip()
                # Avoid grabbing M.R.P offscreens
                if not candidate.lower().startswith(("m.r.p", "mrp")):
                    price_text = candidate

            price_int = parse_price_to_int(price_text)  # returns None if "N/A"

            image_el = card.query_selector("img.s-image")
            image = image_el.get_attribute("src") if image_el else None

            # ----- Rating -----
            rating_el = card.query_selector("span.a-icon-alt")
            rating = rating_el.inner_text().strip() if rating_el else "N/A"

            # ----- Skip obvious non-products -----
            low = title_text.lower()
            if any(w in low for w in ["plan", "cover", "warranty", "gift card"]):
                continue

            # ----- Apply budget filter (only if we have a numeric price) -----
            if max_price is not None and price_int is not None and price_int > max_price:
                continue

            parsed.append(
                {
                    "title": title_text,
                    "price": price_text,
                    "price_value": price_int if price_int is not None else 99999999,
                    "rating": rating,
                    "image": image, 
                    "link": href
                }
            )

        except Exception as e:
            logger.warning(f"Amazon parse failed: {e}")

    # Sort & slice
    parsed.sort(key=lambda x: x.get("price_value", 10**9))
    results = parsed                                                       # results = parsed[:max_results]

    if not results:
        logger.warning("Amazon: No product items parsed after filtering")
    return results
