# server/app/api/auth_oauth.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from sqlmodel import Session, select
from jose import jwt
from datetime import datetime, timedelta, timezone
import bcrypt
import os

from app.db.database import engine
from app.db.models import User

# ──────────────────────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/api/auth", tags=["OAuth"])

config = Config(environ=os.environ)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL  = os.getenv("BACKEND_URL",  "http://localhost:8000")

# IMPORTANT: use the SAME secret/alg as your email/password JWT in auth_routes.py
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM  = "HS256"

oauth = OAuth(config)

# Google
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    client_kwargs={"scope": "openid email profile"},
)

# GitHub (optional)
oauth.register(
    name="github",
    api_base_url="https://api.github.com/",
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    client_kwargs={"scope": "read:user user:email"},
)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _issue_jwt_for_user_id(user_id: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {"sub": str(user_id), "exp": int(exp.timestamp())}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def _set_session_cookie(resp: RedirectResponse, token: str) -> None:
    # For localhost keep secure=False and SameSite=Lax (works with redirects)
    resp.set_cookie(
        key="intelli_session",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
        max_age=60 * 60 * 24 * 7,
    )

def _get_or_create_user(name: str, email: str, avatar_url: str | None) -> User:
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if user:
            changed = False
            if name and user.name != name:
                user.name = name; changed = True
            if avatar_url and user.avatar_url != avatar_url:
                user.avatar_url = avatar_url; changed = True
            if changed:
                session.add(user)
                session.commit()
                session.refresh(user)
            return user

        # create new (password not used for OAuth login)
        hashed = bcrypt.hashpw("oauth".encode(), bcrypt.gensalt()).decode()
        user = User(name=name or email.split("@")[0], email=email, password_hash=hashed, avatar_url=avatar_url)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

# ──────────────────────────────────────────────────────────────────────────────
# Google OAuth
# ──────────────────────────────────────────────────────────────────────────────
@router.get("/google/login", include_in_schema=False)
async def google_login(request: Request):
    redirect_uri = f"{BACKEND_URL}/api/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)  # type: ignore

@router.get("/google/callback", include_in_schema=False)
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)  # type: ignore
    userinfo = token.get("userinfo")
    if not userinfo:
        userinfo = await oauth.google.parse_id_token(request, token)  # type: ignore
    if not userinfo:
        raise HTTPException(status_code=400, detail="Failed to get Google user info")

    email = userinfo.get("email")
    name = userinfo.get("name") or userinfo.get("given_name") or ""
    picture = userinfo.get("picture")
    if not email:
        raise HTTPException(status_code=400, detail="Google did not return an email")

    user = _get_or_create_user(name=name, email=email, avatar_url=picture)

    if not user or user.id is None:
        raise ValueError("Cannot issue token — user not found or missing ID")
    jwt_token = _issue_jwt_for_user_id(user.id)
    resp = RedirectResponse(url=f"{FRONTEND_URL}/")
    _set_session_cookie(resp, jwt_token)
    return resp

# ──────────────────────────────────────────────────────────────────────────────
# GitHub OAuth (optional)
# ──────────────────────────────────────────────────────────────────────────────
@router.get("/github/login", include_in_schema=False)
async def github_login(request: Request):
    redirect_uri = f"{BACKEND_URL}/api/auth/github/callback"
    return await oauth.github.authorize_redirect(request, redirect_uri)  # type: ignore

@router.get("/github/callback", include_in_schema=False)
async def github_callback(request: Request):
    token = await oauth.github.authorize_access_token(request)  # type: ignore
    profile = await oauth.github.get("user", token=token)  # type: ignore
    emails = await oauth.github.get("user/emails", token=token)  # type: ignore

    profile_json = profile.json()
    emails_json = emails.json() if emails else []

    email = None
    if isinstance(emails_json, list) and emails_json:
        primary = next((e for e in emails_json if e.get("primary") and e.get("verified")), None)
        email = (primary or emails_json[0]).get("email")

    if not email:
        raise HTTPException(status_code=400, detail="GitHub did not return a valid email")

    name = profile_json.get("name") or profile_json.get("login") or ""
    avatar = profile_json.get("avatar_url")

    user = _get_or_create_user(name=name, email=email, avatar_url=avatar)


    if not user or user.id is None:
        raise ValueError("Cannot issue token — user not found or missing ID")
    jwt_token = _issue_jwt_for_user_id(user.id)
    resp = RedirectResponse(url=f"{FRONTEND_URL}/")
    _set_session_cookie(resp, jwt_token)
    return resp