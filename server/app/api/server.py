# server/app/api/server.py
import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware

from app.db.database import init_db
from app.api.routes import (
    auth_routes,
    auth_oauth,
    plan_routes,
    search_routes,
    download_routes,
    history_routes,
    proof_routes,
    product_routes,
    compare_routes,
)

load_dotenv()

# Windows Playwright fix (safe no-op on non-Windows)
if os.name == "nt":
    try:
        policy = asyncio.get_event_loop_policy()
        if not isinstance(policy, asyncio.WindowsProactorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception as e:
        print("⚠️ Event loop policy fix failed:", e)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🧱 Creating database tables...")
    init_db()
    print("✅ Database initialized")
    yield
    print("🧹 Server shutting down...")

app = FastAPI(title="AI Web Navigator Backend", lifespan=lifespan)

# ── CORS: allow your frontend to send cookies ────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Starlette session for OAuth "state" (Authlib needs request.session) ──────
# IMPORTANT: use a DIFFERENT cookie name than your auth cookie.
# Never use "intelli_session" here.
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("OAUTH_STATE_SECRET", "oauth-state-secret"),
    session_cookie="starlette_session",       # <-- distinct, safe
    same_site="lax",                          # default is Lax; explicit for clarity
    https_only=False,                         # True only when you run HTTPS
)

@app.get("/health")
def health():
    return {"ok": True, "msg": "Server running"}

# Routers
app.include_router(auth_routes.router)
app.include_router(plan_routes.router)
app.include_router(search_routes.router)
app.include_router(download_routes.router)
app.include_router(history_routes.router)
app.include_router(proof_routes.router)
app.include_router(product_routes.router)
app.include_router(auth_oauth.router)   # OAuth routes
app.include_router(compare_routes.router)