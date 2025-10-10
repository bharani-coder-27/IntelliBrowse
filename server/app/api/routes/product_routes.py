# app/api/routes/product_routes.py
from fastapi import APIRouter
from sqlmodel import Session
from app.db.database import engine
from app.db.crud import get_products_by_search
from app.db.models import Search

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("/{search_id}")
def get_products(search_id: int):
    with Session(engine) as session:
        products = get_products_by_search(session, search_id)
        search = session.get(Search, search_id)  # ✅ fetch the parent search
        intent = search.intent if search else "shop"  # fallback

        return {
            "intent": intent,
            "items": [p.dict() for p in products],
        }
