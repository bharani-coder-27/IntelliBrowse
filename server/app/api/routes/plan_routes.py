# app/api/routes/plan_routes.py
from fastapi import APIRouter, HTTPException
from app.llm.planner import plan_from_instruction
from app.schemas.plan import SearchPlan

router = APIRouter(prefix="/api", tags=["Planner"])

@router.post("/plan", response_model=SearchPlan)
def generate_plan(instruction: dict):
    """
    Convert a natural-language instruction into a structured search plan.
    Example:
      POST /api/plan
      {
        "instruction": "Find top 5 laptops under 50000 from Amazon and Flipkart"
      }
    """
    try:
        text = instruction.get("instruction")
        if not isinstance(text, str) or not text.strip():
            raise HTTPException(status_code=400, detail="Missing or invalid 'instruction'")

        result = plan_from_instruction(text)
        return SearchPlan(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
