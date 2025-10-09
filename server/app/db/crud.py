# app/db/crud.py
from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy import desc
from app.db.models import Search, Product, History, User


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
    Insert a search record + its associated products.
    Used in orchestrate() after a successful agent run.
    """
    query_value: str = plan.get("query") or "unknown query"
    intent_value: Optional[str] = plan.get("intent")
    sources_value: Optional[str] = ",".join(plan.get("sources", [])) if plan.get("sources") else None
    instruction_value: Optional[str] = plan.get("instruction")

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

    # Save all extracted products linked to this search
    for r in results:
        product = Product(
            search_id=search.id,
            title=r.get("title", "N/A"),
            price=r.get("price"),
            rating=r.get("rating"),
            url=r.get("url"),
            source=r.get("source"),
            image=r.get("image"),
            specs=r.get("specs"),
        )
        session.add(product)
    session.commit()

    return search


def get_products_by_search(session: Session, search_id: int) -> List[Product]:
    """Get all products belonging to a particular search."""
    result = session.exec(select(Product).where(Product.search_id == search_id))
    return list(result.all())


# ------------------------------
# 🕓 HISTORY
# ------------------------------
def add_history(session: Session, user_id: int, query: str, intent: str) -> History:
    """Record a user search query in history."""
    history = History(user_id=user_id, query=query, intent=intent)
    session.add(history)
    session.commit()
    session.refresh(history)
    return history


def get_recent_searches(
    session: Session,
    intent: Optional[str] = None,
    user_id: Optional[int] = None
) -> List[Search]:
    """Fetch the 20 most recent searches for a user (optionally filtered by intent)."""
    q = select(Search)
    if intent:
        q = q.where(Search.intent == intent)
    if user_id:
        q = q.where(Search.user_id == user_id)

    q = q.order_by(desc(Search.__table__.c.created_at)).limit(20)
    result = session.exec(q)
    return list(result.all())
