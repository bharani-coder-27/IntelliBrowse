from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/api/proof", tags=["Proof"])
SNAPS_DIR = "runs/snaps"

@router.get("/{filename}")
def get_proof(filename: str):
    path = os.path.join(SNAPS_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Proof not found")
    return FileResponse(path)
