from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from itsdangerous import URLSafeTimedSerializer
from sqlmodel import Session, select
from app.db.database import engine
from app.db.models import User
import bcrypt
import os

# --------------------------------------------------------------------------
# 🧭 Router Setup
# --------------------------------------------------------------------------
router = APIRouter(prefix="/api/auth", tags=["OAuth"])

# --------------------------------------------------------------------------
# 🔧 Environment Config
# --------------------------------------------------------------------------
config = Config(environ=os.environ)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
OAUTH_SECRET_KEY = os.getenv("OAUTH_SECRET_KEY", "oauthsecret")
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "intelli_session")

# --------------------------------------------------------------------------
# ⚙️ OAuth Setup
# --------------------------------------------------------------------------
oauth = OAuth(config)

# Register Google
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    client_kwargs={"scope": "openid email profile"},
)

# Register GitHub
oauth.register(
    name="github",
    api_base_url="https://api.github.com/",
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    client_kwargs={"scope": "read:user user:email"},
)

# Create client instances (Authlib adds them dynamically)
google = oauth.create_client("google")  # type: ignore
github = oauth.create_client("github")  # type: ignore

# --------------------------------------------------------------------------
# 🔒 Cookie Serializer
# --------------------------------------------------------------------------
serializer = URLSafeTimedSerializer(OAUTH_SECRET_KEY)


def set_cookie(resp: RedirectResponse, data: dict):
    token = serializer.dumps(data)
    resp.set_cookie(
        key="intelli_session",
        value=token,
        httponly=True,
        samesite="lax",   # or "none" if frontend runs on a different port
        secure=False,     # True only when HTTPS
        max_age=60 * 60 * 24 * 7,
        path="/",
    )




@router.get("/debug/cookies")
def debug_cookies(request: Request):
    print("🔹 Cookies:", request.cookies)
    return {"cookies": request.cookies}

# --------------------------------------------------------------------------
# 🌐 GOOGLE OAUTH FLOW
# --------------------------------------------------------------------------
@router.get("/google/login")
async def google_login(request: Request):
    """Redirect user to Google for authentication."""
    redirect_uri = f"{BACKEND_URL}/api/auth/google/callback"
    return await google.authorize_redirect(request, redirect_uri)  # type: ignore


@router.get("/google/callback")
async def google_callback(request: Request):
    """Handle Google's OAuth2 callback."""
    token = await google.authorize_access_token(request)  # type: ignore
    userinfo = token.get("userinfo")

    if not userinfo:
        userinfo = await google.parse_id_token(request, token)  # type: ignore

    if not userinfo:
        raise HTTPException(status_code=400, detail="Failed to get Google user info")

    email = userinfo.get("email")
    name = userinfo.get("name", "User")
    picture = userinfo.get("picture")

    if not email:
        raise HTTPException(status_code=400, detail="Google did not return an email")

    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            hashed = bcrypt.hashpw("oauth".encode(), bcrypt.gensalt()).decode()
            user = User(
                name=name,
                email=email,
                password_hash=hashed,
                avatar_url=picture,
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        resp = RedirectResponse(url=f"{FRONTEND_URL}/")
        set_cookie(resp, {"id": user.id, "name": user.name, "email": user.email})
        return resp

# --------------------------------------------------------------------------
# 🐙 GITHUB OAUTH FLOW
# --------------------------------------------------------------------------
@router.get("/github/login")
async def github_login(request: Request):
    """Redirect user to GitHub for authentication."""
    redirect_uri = f"{BACKEND_URL}/api/auth/github/callback"
    return await github.authorize_redirect(request, redirect_uri)  # type: ignore


@router.get("/github/callback")
async def github_callback(request: Request):
    """Handle GitHub's OAuth2 callback."""
    token = await github.authorize_access_token(request)  # type: ignore
    profile = await github.get("user", token=token)  # type: ignore
    emails = await github.get("user/emails", token=token)  # type: ignore

    profile_json = profile.json()
    emails_json = emails.json() if emails else []

    # Extract email
    email = None
    if isinstance(emails_json, list) and emails_json:
        primary = next((e for e in emails_json if e.get("primary")), None)
        email = primary["email"] if primary else emails_json[0]["email"]

    if not email:
        raise HTTPException(status_code=400, detail="GitHub did not return a valid email")

    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            hashed = bcrypt.hashpw("oauth".encode(), bcrypt.gensalt()).decode()
            user = User(
                name=profile_json.get("name") or profile_json.get("login"),
                email=email,
                password_hash=hashed,
                avatar_url=profile_json.get("avatar_url"),
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        resp = RedirectResponse(url=f"{FRONTEND_URL}/")
        set_cookie(resp, {"id": user.id, "name": user.name, "email": user.email})
        return resp
