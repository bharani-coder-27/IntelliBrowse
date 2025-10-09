# app/db/models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

# ---------- USER ----------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    password_hash: str
    avatar_url: Optional[str] = Field(default=None)  # ✅ new field for OAuth profile picture
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # relationships
    searches: List["Search"] = Relationship(back_populates="user")
    histories: List["History"] = Relationship(back_populates="user")


# ---------- SEARCH ----------
class Search(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    query: str
    intent: Optional[str] = None
    sources: Optional[str] = None
    instruction: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="searches")
    products: List["Product"] = Relationship(back_populates="search")


# ---------- PRODUCT ----------
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    search_id: Optional[int] = Field(default=None, foreign_key="search.id")
    title: str
    price: Optional[str] = None
    rating: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    image: Optional[str] = None
    specs: Optional[str] = None

    search: Optional[Search] = Relationship(back_populates="products")


# ---------- HISTORY ----------
class History(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    query: str
    intent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="histories")
