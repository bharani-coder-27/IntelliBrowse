# app/api/server.py
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.api.routes import (
    auth_oauth, compare_routes, plan_routes, search_routes, download_routes,
    history_routes, proof_routes, product_routes, auth_routes, auth_oauth, compare_routes
)
from starlette.middleware.sessions import SessionMiddleware
import os


load_dotenv()

# ✅ Windows Playwright fix
if asyncio.get_event_loop_policy().__class__.__name__ != "ProactorEventLoopPolicy":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

@asynccontextmanager
async def lifespan(app):
    init_db()
    print("✅ Database initialized")
    yield
    print("🧹 Server shutting down...")

app = FastAPI(title="AI Web Navigator Backend", lifespan=lifespan)

# ✅ Allow frontend origin
origins = [
    "http://localhost:8000",  # Vite dev server
    "http://127.0.0.1:8000",
]

# ✅ Add SessionMiddleware (required for OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("OAUTH_SECRET_KEY", "oauthsecret"),  # same as in .env
    session_cookie="intelli_session",
)


# ✅ Allow credentials in CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True, "msg": "Server running"}

# ✅ Include modular routes
app.include_router(auth_routes.router)
app.include_router(plan_routes.router)
app.include_router(search_routes.router)
app.include_router(download_routes.router)
app.include_router(history_routes.router)
app.include_router(proof_routes.router)
app.include_router(product_routes.router)
app.include_router(auth_oauth.router)
app.include_router(compare_routes.router)
