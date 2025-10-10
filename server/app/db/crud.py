# app/db/crud.py
from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy import desc
from app.db.models import Search, Product, History, User
from datetime import datetime

# ------------------------------
# 🔐 USERS
# ------------------------------
def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Fetch a user by email."""
    result = session.exec(select(User).where(User.email == email))
    return result.first()


def add_user(session: Session, name: str, email: str, password_hash: str) -> User:
    """Create a new user record."""
    user = User(name=name, email=email, password_hash=password_hash)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# ------------------------------
# 🔍 SEARCHES
# ------------------------------
def add_search(session: Session, plan: dict, results: list[dict], user_id: Optional[int] = None) -> Search:
    """
    Inserts a search record + its associated products or web results.
    Handles both 'shop' (Amazon/Flipkart) and 'explore/learn' (Wikipedia/web).
    """
    query_value = plan.get("query") or "unknown"
    intent_value = plan.get("intent")
    sources_value = ",".join(plan.get("sources", [])) if plan.get("sources") else None
    instruction_value = plan.get("instruction")

    # ✅ Create the Search record
    search = Search(
        user_id=user_id,
        instruction=instruction_value,
        query=query_value,
        intent=intent_value,
        sources=sources_value,
    )
    session.add(search)
    session.commit()
    session.refresh(search)

    # ✅ Store each result depending on intent
    for r in results:
        # For explore/learn — Wikipedia or info type
        if intent_value in ("explore", "learn"):
            product = Product(
                search_id=search.id,
                title=r.get("title", "Untitled"),
                url=r.get("url"),
                source=r.get("site", "web"),
                text=r.get("text"),        # 🧠 Store the summarized text
                price=None,
                rating=None,
                image=None,
                specs=None,
            )

        # For shop — product type
        else:
            product = Product(
                search_id=search.id,
                title=r.get("title", "Untitled"),
                price=r.get("price"),
                rating=r.get("rating"),
                url=r.get("link"),
                source=r.get("source"),
                image=r.get("image"),
                specs=r.get("specs"),
            )

        session.add(product)

    session.commit()
    return search


def add_history(session: Session, user_id: int, query: str, intent: str):
    """Adds a record to user search history."""
    history = History(user_id=user_id, query=query, intent=intent)
    session.add(history)
    session.commit()
    return history


def get_products_by_search(session: Session, search_id: int) -> List[Product]:
    """Returns all stored items (products or summaries) for a given search."""
    result = session.exec(select(Product).where(Product.search_id == search_id))
    return list(result.all())


def get_recent_searches(
    session: Session,
    intent: Optional[str] = None,
    user_id: Optional[int] = None
) -> List[History]:
    """Fetch the 20 most recent searches for a user (optionally filtered by intent)."""
    q = select(History)
    if intent:
        q = q.where(History.intent == intent)
    if user_id:
        q = q.where(History.user_id == user_id)

    q = q.order_by(desc(History.__table__.c.timestamp)).limit(20)
    result = session.exec(q)
    return list(result.all())
