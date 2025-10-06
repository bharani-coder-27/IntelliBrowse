# app/skills/extractors/__init__.py
from typing import List, Dict, Optional
from app.browser.controller import BrowserController
from app.skills.extractors.amazon import extract_amazon_products
from app.skills.extractors.flipkart import extract_flipkart_products
from app.skills.extractors.web import extract_web_results  # for learn/news

def extract_products_or_info(
    bc: Optional[BrowserController],
    source: str,
    query: str,
    max_results: int = 10,
    max_price: Optional[int] = None
) -> List[Dict]:
    s = source.lower().strip()
    if s in ("amazon","amz"):
        return extract_amazon_products(bc, max_results=max_results, query=query, max_price=max_price)
    if s in ("flipkart","fk"):
        return extract_flipkart_products(bc, max_results=max_results, query=query, max_price=max_price)
    if s in ("web",):
        return extract_web_results(query=query, max_results=max_results)
    raise ValueError(f"Unsupported source: {source}")
