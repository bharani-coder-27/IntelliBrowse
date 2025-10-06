# app/db/crud.py
from typing import List
from sqlmodel import Session, select
from app.db.models import SearchHistory, Product
from typing import List, Optional

def add_search(session: Session, plan: dict, items: List[dict], paths: dict):
    """Insert new search and related products"""
    history = SearchHistory(
        instruction=plan.get("instruction"),
        query=plan.get("query"),
        sources=",".join(plan.get("sources", [])),
        intent=plan.get("intent", "shop"),
        max_price=plan.get("max_price"),
        result_count=len(items),
        json_path=paths.get("json_path"),
        csv_path=paths.get("csv_path"),
    )
    session.add(history)
    session.commit()
    session.refresh(history)

    # Store products
    for item in items:
        p = Product(
            search_id=history.id,
            title=item.get("title"),
            price=item.get("price"),
            price_value=item.get("price_value"),
            rating=item.get("rating"),
            link=item.get("link"),
            site=item.get("site"),
            image_path=item.get("image_path"),
            proof_path=item.get("proof_path"),
        )
        session.add(p)
    session.commit()
    return history


def get_recent_searches(session: Session, limit=10, intent: Optional[str] = None):
    from sqlmodel import select
    stmt = select(SearchHistory)
    if intent:
        stmt = stmt.where(SearchHistory.intent == intent)
    stmt = stmt.order_by(SearchHistory.created_at.desc()).limit(limit)
    return session.exec(stmt).all()


def get_products_by_search(session: Session, search_id: int):
    """Return all products for a given search ID"""
    stmt = select(Product).where(Product.search_id == search_id)
    return session.exec(stmt).all()
