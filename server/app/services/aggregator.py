# app/services/aggregator.py
from typing import List, Dict, Optional
from app.browser.controller import BrowserController
from app.skills.extractors import extract_products_or_info
from app.services.utils import dedupe, sort_by_price
from app.utils.logger import logger
import traceback


def search_products(
    bc: BrowserController,
    sources: list[str],        # e.g., ["amazon"], ["flipkart"], or ["amazon", "flipkart"]
    query: str,
    max_results: int = 10,
    max_price: Optional[int] = None,
) -> List[Dict]:
    """
    Aggregate product data from multiple e-commerce extractors (Amazon, Flipkart, etc.)
    and return a unified, deduplicated, sorted list.
    """
    all_items: List[Dict] = []

    for src in sources:
        try:
            logger.info(f"🔎 Extracting from {src.title()} for query: {query!r}")
            chunk = extract_products_or_info(
                bc=bc,
                source=src,
                query=query,
                max_results=max_results,  # per-site overfetch
                max_price=max_price,
            )

            # tag site for clarity
            for r in chunk:
                r.setdefault("site", src.lower())

            all_items.extend(chunk)
            logger.info(f"✅ {len(chunk)} items fetched from {src.title()}")

        except Exception as e:
            logger.warning(f"⚠️ {src.title()} extractor failed: {e}")
            traceback.print_exc()

    # ✅ Deduplicate by title + price
    items = dedupe(all_items)

    # ✅ Sort by numeric price
    items = sort_by_price(items)

    # ✅ Limit to max_results total
    final = items

    logger.info(f"🧮 Aggregated {len(final)} total products after dedupe & sort")
    return final
