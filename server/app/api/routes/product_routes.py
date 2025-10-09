from fastapi import APIRouter
from sqlmodel import Session
from app.db.database import engine
from app.db.crud import get_products_by_search

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("/{search_id}")
def get_products(search_id: int):
    with Session(engine) as session:
        products = get_products_by_search(session, search_id)
        return {"items": [p.dict() for p in products]}
