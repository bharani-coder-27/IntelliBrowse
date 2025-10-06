# app/db/models.py
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class SearchHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    instruction: str
    query: str
    sources: str                  # e.g. "amazon,flipkart" or "web"
    intent: str                   # shop / learn / explore / news
    max_price: Optional[int] = None
    result_count: int = 0
    json_path: Optional[str] = None
    csv_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    search_id: int = Field(foreign_key="searchhistory.id")
    title: str
    price: Optional[str] = None
    price_value: Optional[int] = None
    rating: Optional[str] = None
    link: str
    site: Optional[str] = None
    image_path: Optional[str] = None
    proof_path: Optional[str] = None

class Proof(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    selector: Optional[str] = None
    screenshot_path: Optional[str] = None
    captured_at: datetime = Field(default_factory=datetime.utcnow)
