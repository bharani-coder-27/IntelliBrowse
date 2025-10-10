from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from app.db.database import engine
from app.db.crud import get_recent_searches
from app.api.dependencies.auth import get_current_user  # ✅ make sure you have this

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("/")
def get_history(
    intent: str | None = Query(None),
    user_id: int = Depends(get_current_user)
):
    """
    Fetch up to 20 most recent searches made by the logged-in user.
    Optional filter: intent (shop / learn / explore)
    """
    with Session(engine) as session:
        records = get_recent_searches(session, intent=intent, user_id=user_id)
        return {"history": [r.dict() for r in records]}
