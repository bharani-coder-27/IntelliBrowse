# app/api/routes/compare_routes.py
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
from app.db.models import Product
from app.db.database import get_session
from app.utils.summarizer import summarize_comparison

router = APIRouter(prefix="/api/compare", tags=["Compare"])


# ---------- Request Schema ----------
class CompareRequest(BaseModel):
    # product IDs selected from frontend
    ids: List[int]


# ---------- Endpoint ----------
@router.post("/", summary="Compare selected products and return AI summary")
def compare_products(
    body: CompareRequest,
    include_summary: bool = Query(True, description="Return LLM summary"),
    session: Session = Depends(get_session),
):
    """
    Compare selected products by their IDs.
    Returns both raw product data and an optional AI-generated comparison summary.
    """

    # Step 1️⃣ – Basic validation
    product_ids = body.ids or []
    print("The got Ids: ",product_ids)
    print()
    if len(product_ids) < 2:
        raise HTTPException(status_code=400, detail="Select at least two products to compare.")
    if len(product_ids) > 5:
        raise HTTPException(status_code=400, detail="You can compare up to five products only.")

    # Step 2️⃣ – Fetch products from DB
    # (ignore type warning: SQLAlchemy's Column.in_() is resolved at runtime)
    statement = select(Product).where(Product.id.in_(product_ids))  # type: ignore[attr-defined]
    products = session.exec(statement).all()

    print("The products are: ", products)

    if not products or len(products) < 2:
        raise HTTPException(status_code=404, detail="Not enough products found for comparison.")

    # Step 3️⃣ – Convert to dicts for frontend
    product_dicts = []
    for p in products:
        product_dicts.append({
            "id": p.id,
            "search_id": p.search_id,
            "title": p.title,
            "price": p.price,
            "rating": p.rating,
            "url": p.url,
            "source": p.source,
            "image": p.image,
            "specs": p.specs,
        })
    
    print("The compared Products are: ",product_dicts)

    # Step 4️⃣ – Optional AI summary
    summary: Optional[str] = None
    if include_summary:
        try:
            summary = summarize_comparison(product_dicts)
        except Exception as e:
            summary = f"⚠️ LLM summary failed: {e}"
    print("The summary: ", summary)

    # Step 5️⃣ – Return unified response
    return {
        "total_compared": len(product_dicts),
        "products": product_dicts,
        "summary": summary,
        "message": "✅ Product comparison completed successfully."
    }
