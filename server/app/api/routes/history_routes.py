from fastapi import APIRouter, Query
from sqlmodel import Session
from app.db.database import engine
from app.db.crud import get_recent_searches

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("/")
def get_history(intent: str | None = Query(None)):
    with Session(engine) as session:
        records = get_recent_searches(session, intent=intent)
        return {"history": [r.dict() for r in records]}
