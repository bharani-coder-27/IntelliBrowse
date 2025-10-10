# server/app/api/auth_routes.py
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import bcrypt
import os

from app.db.database import engine
from app.db.models import User
from app.api.dependencies.auth import get_current_user  # keeps your existing dependency

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# ──────────────────────────────────────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────────────────────────────────────
class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    avatar_url: str | None = None

# ──────────────────────────────────────────────────────────────────────────────
# Helpers (JWT + cookie utilities)
# ──────────────────────────────────────────────────────────────────────────────
def _issue_jwt_for_user_id(user_id: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=7)
    return jwt.encode({"sub": str(user_id), "exp": int(exp.timestamp())}, SECRET_KEY, algorithm=ALGORITHM)

def _set_session_cookie(resp: JSONResponse, token: str) -> None:
    # For localhost: keep secure=False and SameSite=Lax (works with redirects)
    resp.set_cookie(
        key="intelli_session",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
        max_age=60 * 60 * 24 * 7,
    )

def _clear_session_cookie(resp: JSONResponse) -> None:
    # Mirror attributes used when setting for reliable deletion
    resp.delete_cookie(
        key="intelli_session",
        path="/",
        samesite="lax",
        secure=False,
    )

def _to_user_out(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "avatar_url": user.avatar_url,
    }

# ──────────────────────────────────────────────────────────────────────────────
# Register → creates user, logs them in (sets cookie), returns sanitized user
# ──────────────────────────────────────────────────────────────────────────────
@router.post("/register")
def register(data: RegisterIn):
    with Session(engine) as session:
        exists = session.exec(select(User).where(User.email == data.email)).first()
        if exists:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
        user = User(name=data.name, email=data.email, password_hash=hashed)
        session.add(user)
        session.commit()
        session.refresh(user)
        if not user or user.id is None:
            raise ValueError("Cannot issue token — user not found or missing ID")

        token = _issue_jwt_for_user_id(user.id)
        resp = JSONResponse({"user": _to_user_out(user)})
        _set_session_cookie(resp, token)
        return resp

# ──────────────────────────────────────────────────────────────────────────────
# Login → verifies, sets cookie, returns sanitized user
# ──────────────────────────────────────────────────────────────────────────────
@router.post("/login")
def login(data: LoginIn):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == data.email)).first()
        if not user or not user.password_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not bcrypt.checkpw(data.password.encode(), user.password_hash.encode()):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not user or user.id is None:
            raise ValueError("Cannot issue token — user not found or missing ID")

        token = _issue_jwt_for_user_id(user.id)
        resp = JSONResponse({"user": _to_user_out(user)})
        _set_session_cookie(resp, token)
        return resp

# ──────────────────────────────────────────────────────────────────────────────
# Me → uses your existing dependency which reads/validates JWT from cookie
# ──────────────────────────────────────────────────────────────────────────────
@router.get("/me")
def me(request: Request, user_id: int = Depends(get_current_user)):
    with Session(engine) as session:
        # Optional: debug cookies in dev
        # print("🔹 Cookies received:", request.cookies)
        user = session.get(User, user_id)
        if not user:
            return {"user": None}
        return {"user": _to_user_out(user)}

# ──────────────────────────────────────────────────────────────────────────────
# Logout → clears the cookie
# ──────────────────────────────────────────────────────────────────────────────
@router.post("/logout")
def logout():
    resp = JSONResponse({"ok": True, "message": "Logged out successfully"})
    _clear_session_cookie(resp)
    return resp