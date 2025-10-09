# app/api/routes/download_routes.py
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from app.db.database import engine
from app.db.models import Search, Product
from app.api.dependencies.auth import get_current_user
from app.utils.export_utils import export_to_csv, export_to_json

router = APIRouter(prefix="/api/download", tags=["Download"])

@router.get("/{format}")
def download_results(
    format: str,
    search_id: int = Query(..., description="Search ID to export"),
    user_id: int = Depends(get_current_user)
):
    """Dynamically fetch results for a given search and stream CSV/JSON."""
    format = format.lower()
    if format not in ["csv", "json"]:
        raise HTTPException(status_code=400, detail="Invalid format. Use csv or json.")

    with Session(engine) as session:
        search = session.exec(select(Search).where(Search.id == search_id, Search.user_id == user_id)).first()
        if not search:
            raise HTTPException(status_code=404, detail="Search not found or not authorized")

        products = session.exec(select(Product).where(Product.search_id == search_id)).all()
        data = [p.dict() for p in products]

        filename = f"{search.intent or 'search'}_{search.query.replace(' ', '_')}"

        if format == "json":
            return export_to_json(data, filename)
        else:
            return export_to_csv(data, filename)
