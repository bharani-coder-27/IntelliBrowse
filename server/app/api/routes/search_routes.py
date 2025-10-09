# app/api/routes/search_routes.py
import os, json, time, traceback
from fastapi import APIRouter, HTTPException, Depends
from playwright.sync_api import Error, TimeoutError
from sqlmodel import Session
from app.db.database import engine
from app.browser.controller import BrowserController
from app.services.aggregator import search_products
from app.skills.extractors import extract_products_or_info
from app.llm.planner import plan_from_instruction
from app.db.crud import add_search, add_history, get_products_by_search
from app.api.dependencies.auth import get_current_user  # ✅ user auth dependency

router = APIRouter(prefix="/api", tags=["Search"])


@router.post("/orchestrate")
def orchestrate(body: dict, user_id: int = Depends(get_current_user)):
    """
    Orchestrates the AI web navigation flow:
    1. Generate plan from LLM
    2. Normalize sources
    3. Fetch results (browser or info)
    4. Save everything in DB
    5. Return results
    """
    try:
        instruction = (body.get("instruction") or "").strip()
        if not instruction:
            raise HTTPException(status_code=400, detail="Missing 'instruction' in request body")

        # 1️⃣ Step — Generate LLM plan
        plan = plan_from_instruction(instruction)
        print("🧠 Plan of the Agent:", json.dumps(plan, indent=2))

        # ✅ 1.1 — Normalize and auto-correct sources
        valid_sources = {"amazon", "flipkart", "web"}
        plan["sources"] = [s.lower() for s in plan.get("sources", []) if s.lower() in valid_sources]

        # If learn intent accidentally got amazon/flipkart, switch to web
        if plan["intent"] in ("learn", "explore") and "web" not in plan["sources"]:
            print("⚠️ Auto-correcting sources for learn intent → ['web']")
            plan["sources"] = ["web"]

        # If shop intent has no valid source, fallback to both
        if plan["intent"] == "shop" and not any(s in ("amazon", "flipkart") for s in plan["sources"]):
            plan["sources"] = ["amazon", "flipkart"]

        # 2️⃣ Step — Run browser extraction (with retry)
        results = []
        if plan["intent"] == "shop":
            for attempt in range(2):  # retry browser once
                try:
                    with BrowserController(run_dir="runs") as bc:
                        results = search_products(
                            bc=bc,
                            sources=plan["sources"],
                            query=plan["query"],
                            max_results=plan["max_results"],
                            max_price=plan["max_price"],
                        )
                    break
                except Exception as browser_error:
                    print(f"\n[Attempt {attempt+1}] Browser extraction failed:\n")
                    traceback.print_exc()
                    if attempt == 0:
                        print("🔁 Retrying once more...\n")
                        time.sleep(2)
                        continue
                    else:
                        raise RuntimeError(f"Browser failed twice: {browser_error}")
        else:
            # 3️⃣ Step — Web/info extraction (no browser)
            for src in plan["sources"]:
                results += extract_products_or_info(None, src, plan["query"], plan["max_results"])

        if not results:
            print("⚠️ No results fetched for:", plan["query"])

        # 4️⃣ Step — Save everything in DB
        with Session(engine) as session:
            # save search + products
            search_entry = add_search(
                session,
                {**plan, "instruction": instruction},
                results,
                user_id=user_id
            )

            # record search in history
            add_history(session, user_id, plan["query"], plan["intent"])

            if search_entry.id is None:
                raise RuntimeError("Search ID not generated — database commit failed.")

            # store id before closing session
            search_id = search_entry.id

            # ✅ fetch all products inserted for this search
            product_rows = get_products_by_search(session, search_id)
            product_ids = [p.id for p in product_rows]

        print("These are the product IDs: ",product_ids)
        # ✅ unified structured response
        return {
            "plan": plan,
            "total": len(product_rows),
            "search_id": search_id,
            "product_ids": [p.id for p in product_rows],  # ✅ include this,             # 🆕 added field for frontend
            "items": results,
            "message": "✅ Results stored successfully in database."
        }


    except TimeoutError:
        raise HTTPException(status_code=503, detail="Network timeout — target site not reachable.")
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Playwright error: {e}")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
