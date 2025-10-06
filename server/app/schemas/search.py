from typing import Optional, Literal, List
from pydantic import BaseModel

SourceType = Literal["amazon", "flipkart", "both", "web"]

class SearchRequest(BaseModel):
    source: Optional[SourceType] = "both"
    query: str
    max_results: int = 10
    max_price: Optional[int] = None
    headless: bool = True


class Product(BaseModel):
    title: str
    price: str
    price_value: Optional[int] = None
    rating: Optional[str] = None
    link: str
    site: Optional[str] = None


class SearchResponse(BaseModel):
    items: List[Product]
    total: int
