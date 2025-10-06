# app/api/server.py
import asyncio

# ✅ Fix Playwright subprocess issue on Windows
if asyncio.get_event_loop_policy().__class__.__name__ != "ProactorEventLoopPolicy":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os, json, glob
from contextlib import asynccontextmanager
from fastapi import Query
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import time
import traceback
from playwright.sync_api import Error, TimeoutError
import socket

from app.llm.planner import plan_from_instruction
from app.schemas.plan import SearchPlan
from app.schemas.search import SearchRequest, SearchResponse, Product
from app.browser.controller import BrowserController
from app.services.aggregator import search_products
from app.services.utils import save_json, save_csv, ensure_dir
from app.skills.extractors import extract_products_or_info   # ✅ added import

from app.db.database import init_db
from sqlmodel import Session
from app.db.database import engine
from app.db.crud import add_search, get_recent_searches

load_dotenv()

# ✅ Modern lifespan pattern
@asynccontextmanager
async def lifespan(app):
    init_db()
    print("✅ Database initialized")
    yield
    print("🧹 Server shutting down...")

app = FastAPI(title="AI Web Navigator Backend", lifespan=lifespan)

# ✅ Allow frontend origin
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # List of trusted origins
    allow_credentials=True,
    allow_methods=["*"],          # Allow all HTTP methods
    allow_headers=["*"],          # Allow all headers
)


@app.get("/health")
def health():
    return {"ok": True, "msg": "Server running"}

#@app.post("/plan", response_model=SearchPlan)
def plan(instruction: dict):
    try:
        text = instruction.get("instruction")
        if not isinstance(text, str) or not text.strip():
            raise HTTPException(status_code=400, detail="Missing or invalid instruction text")

        result = plan_from_instruction(text)
        return SearchPlan(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2️⃣ Run search directly (source: amazon, flipkart, both)
@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    try:
        os.environ["HEADLESS"] = "true" if req.headless else "false"

        # ✅ Ensure source is never None
        source = req.source or "both"

        with BrowserController(run_dir="runs") as bc:
            items = search_products(
                bc=bc,
                sources=[source] if source != "both" else ["amazon", "flipkart"],
                query=req.query,
                max_results=req.max_results,
                max_price=req.max_price,
            )

        return SearchResponse(items=[Product(**i) for i in items], total=len(items))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")


@app.post("/orchestrate")
def orchestrate(body: dict):
    try:
        instruction = (body.get("instruction") or "").strip()
        if not instruction:
            raise HTTPException(status_code=400, detail="Missing 'instruction' in request body")

        # 1️⃣ Step — Generate LLM plan
        plan = plan_from_instruction(instruction)
        print("🧠 Plan of the Agent:", json.dumps(plan, indent=2))

        ensure_dir("data")

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
            for attempt in range(2):  # retry browser creation once
                try:
                    with BrowserController(run_dir="runs") as bc:
                        results = search_products(
                            bc=bc,
                            sources=plan["sources"],
                            query=plan["query"],
                            max_results=plan["max_results"],
                            max_price=plan["max_price"],
                        )
                    break  # ✅ Success
                except Exception as browser_error:
                    print(f"\n[Attempt {attempt+1}] Browser extraction failed with error:\n")
                    traceback.print_exc()  # ✅ show full error message
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

        # 4️⃣ Step — Save results
        base = f"{plan['intent']}_{'+'.join(plan['sources'])}_{plan['query'].replace(' ', '_')}"
        json_path = save_json(results, "data", base)
        csv_path = save_csv(results, "data", base)

        # 5️⃣ Step — Persist in DB
        try:
            with Session(engine) as session:
                add_search(
                    session,
                    {**plan, "instruction": instruction},
                    results,
                    {"json_path": json_path, "csv_path": csv_path},
                )
        except Exception as db_error:
            print(f"⚠️ DB save skipped (error: {db_error})")

        # 6️⃣ Step — Return final response
        return {
            "plan": plan,
            "total": len(results),
            "json_path": json_path,
            "csv_path": csv_path,
            "download_json": f"/download/json/{os.path.basename(json_path)}",
            "download_csv": f"/download/csv/{os.path.basename(csv_path)}",
            "items": results,
        }

    except TimeoutError:
        raise HTTPException(status_code=503, detail="Network timeout — target site not reachable.")
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Playwright error: {e}")



# 4️⃣ History endpoint (saved files)

@app.get("/history")
def get_history(intent: Optional[str] = Query(None, description="Filter by intent: shop, learn, explore, news")):
    from sqlmodel import Session
    from app.db.database import engine

    with Session(engine) as session:
        records = get_recent_searches(session, intent=intent)
        return {"history": [r.dict() for r in records]}


# 5️⃣ Proof endpoint (show screenshot)
@app.get("/proof/{filename}")
def get_proof(filename: str):
    path = os.path.join("runs/snaps", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Proof not found")
    return FileResponse(path)


@app.get("/products/{search_id}")
def get_products(search_id: int):
    from sqlmodel import Session
    from app.db.database import engine
    from app.db.crud import get_products_by_search

    with Session(engine) as session:
        products = get_products_by_search(session, search_id)
        return {"items": [p.dict() for p in products]}


DATA_DIR = "data"

@app.get("/download/json/{filename}")
def download_json(filename: str):
    """Serve JSON file from /data folder"""
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="JSON file not found")
    return FileResponse(file_path, media_type="application/json", filename=filename)

@app.get("/download/csv/{filename}")
def download_csv(filename: str):
    """Serve CSV file from /data folder"""
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="CSV file not found")
    return FileResponse(file_path, media_type="text/csv", filename=filename)


