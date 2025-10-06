# app/agent/planner.py
import json
from typing import Dict, Any
from app.llm.provider import LLMClient
from app.llm.prompts import SYSTEM, USER_TEMPLATE

def _parse_int_rupees(x):
    """Convert strings like '₹50k', '60,000', 'Rs.75K' → integer or None."""
    if x is None:
        return None
    s = str(x).lower().strip()
    s = s.replace("₹", "").replace(",", "").replace("rs.", "").replace("rs", "").strip()
    if s.endswith("k"):
        s = s[:-1]
        if s.replace(".", "", 1).isdigit():
            return int(float(s) * 1000)
    return int(s) if s.isdigit() else None


def plan_from_instruction(instruction: str) -> Dict[str, Any]:
    """Generate normalized plan from user instruction via LLM."""
    llm = LLMClient()
    user_prompt = USER_TEMPLATE.format(instruction=instruction)

    content = llm.chat(
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
    )

    print("🧠 Raw LLM Response:", content)

    # --- Parse JSON safely ---
    try:
        data = json.loads(content)
    except Exception:
        data = {}

    # --- Extract fields with fallbacks ---
    intent = (data.get("intent") or "").lower().strip()
    sources = data.get("sources") or []
    query = (data.get("query") or instruction).strip()
    max_results = data.get("max_results") or 10
    max_price = _parse_int_rupees(data.get("max_price"))

    # --- Type safety ---
    if not isinstance(sources, list):
        sources = [str(sources)]

    valid_sources = {"amazon", "flipkart", "web"}
    sources = [s for s in sources if s in valid_sources]

    # --- Smart defaults ---
    if not intent:
        # fallback only if model fails to output
        q = query.lower()
        if any(word in q for word in ["buy", "price", "deal", "phone", "laptop"]):
            intent = "shop"
        elif any(word in q for word in ["news", "update", "today"]):
            intent = "news"
        elif any(word in q for word in ["place", "visit", "university", "explore"]):
            intent = "explore"
        else:
            intent = "learn"

    if not sources:
        sources = ["amazon", "flipkart"] if intent == "shop" else ["web"]

    # Ensure max_results is sane
    try:
        max_results = int(max_results)
        if not (1 <= max_results <= 50):
            max_results = 10
    except Exception:
        max_results = 10

    # --- Final output ---
    plan = {
        "intent": intent,
        "sources": sorted(set(sources)),
        "query": query,
        "max_results": max_results,
        "max_price": max_price,
    }

    print("✅ Normalized Plan:", plan)
    return plan
