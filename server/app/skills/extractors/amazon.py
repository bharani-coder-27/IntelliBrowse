from typing import List, Dict, Optional
from urllib.parse import quote_plus
from app.utils.logger import logger
from app.browser.controller import BrowserController
from app.utils.money import parse_price_to_int
from anyio import to_thread

def _norm_link(href: Optional[str]) -> Optional[str]:
    if not href:
        return None
    return href if href.startswith("http") else f"https://www.amazon.in{href}"

# cast(BrowserContext, bc.context).new_page()

from playwright.sync_api import BrowserContext
from typing import Optional, cast

from typing import Optional, cast
from playwright.sync_api import BrowserContext
from app.browser.controller import BrowserController

def _extract_amazon_details(bc: BrowserController, url: str) -> Optional[str]:
    """Fetch full technical details from an Amazon.in product page."""
    try:
        # open a fresh tab safely
        page = cast(BrowserContext, bc.context).new_page()
        page.goto(url, timeout=30_000, wait_until="domcontentloaded")

        # give time for Amazon dynamic load
        page.wait_for_selector("body", timeout=10_000)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")  # scroll mid-page
        page.wait_for_timeout(2000)  # wait 2s to allow lazy sections to load

        details = []

        # 1️⃣ try main technical details table
        selectors = [
            "div.a-expander-content.a-expander-section-content table#productDetails_techSpec_section_1 tr",
            "table#productDetails_techSpec_section_1 tr",
            "table.prodDetTable tr",  # backup generic
        ]

        found_rows = None
        for sel in selectors:
            try:
                if page.query_selector(sel):
                    page.wait_for_selector(sel, timeout=8000)
                    found_rows = page.query_selector_all(sel)
                    break
            except Exception:
                continue

        if not found_rows:
            print(f"⚠️ No spec table found for {url}")
            page.close()
            return None

        tech_lines = []
        for r in found_rows:
            key_el = r.query_selector("th")
            val_el = r.query_selector("td")
            if key_el and val_el:
                key = key_el.inner_text().strip().replace("\n", " ")
                val = val_el.inner_text().strip().replace("\n", " ")
                if key and val:
                    tech_lines.append(f"{key}: {val}")

        if tech_lines:
            details.append("\n".join(tech_lines))

        # 2️⃣ Optional — add “About this item”
        try:
            about_el = page.query_selector("#feature-bullets ul")
            if about_el:
                about_text = about_el.inner_text().strip()
                details.append("About this item:\n" + about_text)
        except Exception:
            pass

        page.close()
        return "\n\n".join(details).strip() if details else None

    except Exception as e:
        print(f"⚠️ Amazon detail extraction failed for {url}: {e}")
        return None


def extract_amazon_products(
    bc: Optional[BrowserController],
    max_results: int = 5,
    query: Optional[str] = None,
    max_price: Optional[int] = None,
) -> List[Dict]:
    logger.info(f"[DEBUG] Entering {__name__} extractor. bc={bc}, page_valid={getattr(bc, 'page', None) is not None}")
    assert bc is not None and bc.page is not None, "BrowserController or page not initialized"

    results: List[Dict] = []

    q = quote_plus(query or "laptops under 50000")
    url = f"https://www.amazon.in/s?k={q}"
    logger.info(f"Navigating Amazon: {url}")
    bc.goto(url, timeout=60_000)

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
    for card in cards[: max_results * 4]:
        try:
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

            if not href:
                dp_link = card.query_selector('a[href*="/dp/"]')
                if dp_link:
                    href = _norm_link(dp_link.get_attribute("href"))
                    if not title_text:
                        maybe_title = (dp_link.inner_text() or "").strip()
                        title_text = maybe_title or title_text

            if not title_text:
                img = card.query_selector("img.s-image[alt]")
                if img:
                    title_text = img.get_attribute("alt")

            if not href or not title_text:
                continue

            price_text = "N/A"
            price_el = (
                card.query_selector('span.a-price[data-a-color="base"] span.a-offscreen')
                or card.query_selector('span.a-price:not(.a-text-price) span.a-offscreen')
                or card.query_selector("span.a-price span.a-offscreen")
            )
            if price_el:
                candidate = price_el.inner_text().strip()
                if not candidate.lower().startswith(("m.r.p", "mrp")):
                    price_text = candidate

            price_int = parse_price_to_int(price_text)
            image_el = card.query_selector("img.s-image")
            image = image_el.get_attribute("src") if image_el else None
            rating_el = card.query_selector("span.a-icon-alt")
            rating = rating_el.inner_text().strip() if rating_el else "N/A"

            low = title_text.lower()
            if any(w in low for w in ["plan", "cover", "warranty", "gift card"]):
                continue

            if max_price is not None and price_int is not None and price_int > max_price:
                continue
            
            specs = None
            parsed.append(
                {
                    "title": title_text,
                    "price": price_text,
                    "price_value": price_int if price_int is not None else 99999999,
                    "rating": rating,
                    "image": image,
                    "specs": specs,
                    "link": href,
                    "source": "amazon",
                }
            )

        except Exception as e:
            logger.warning(f"Amazon parse failed: {e}")

    print("The parsed Data are: ", parsed[0])
    parsed.sort(key=lambda x: x.get("price_value", 10**9))
    results = parsed

    if not results:
        logger.warning("Amazon: No product items parsed after filtering")
    return results
