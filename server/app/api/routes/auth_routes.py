from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
import bcrypt, os
from jose import jwt
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select
from app.db.database import engine
from app.db.models import User
from app.api.dependencies.auth import get_current_user
from fastapi.responses import JSONResponse

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# ---------- Schemas ----------
class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# ---------- Register ----------
@router.post("/register")
def register(data: UserRegister):
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == data.email)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
        user = User(name=data.name, email=data.email, password_hash=hashed)
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"message": "User registered successfully", "user": user.dict()}

# ---------- Login ----------

@router.post("/login")
def login(data: UserLogin):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == data.email)).first()
        if not user or not bcrypt.checkpw(data.password.encode(), user.password_hash.encode()):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        expire_time = datetime.now(timezone.utc) + timedelta(days=7)
        token = jwt.encode(
            {"sub": str(user.id), "exp": int(expire_time.timestamp())},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

        # ✅ Instead of returning token, set it as a cookie
        resp = JSONResponse({
            "message": "Login successful",
            "user": {"id": user.id, "name": user.name, "email": user.email},
        })
        resp.set_cookie(
            key="intelli_session",
            value=token,
            httponly=True,
            samesite="lax",  # or "none" if cross-site
            secure=False,     # set True in production with HTTPS
            max_age=60 * 60 * 24 * 7,
            path="/",
        )
        return resp

# ---------- Me ----------
@router.get("/me")
def me(request: Request, user_id: int = Depends(get_current_user)):
    with Session(engine) as session:
        print("🔹 Cookies received:", request.cookies)
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            return {"user": None}
        return {"user": {"id": user.id, "name": user.name, "email": user.email, "avatar_url": user.avatar_url}}

# ---------- Logout ----------
@router.post("/logout")
def logout():
    resp = JSONResponse({"message": "Logged out successfully"})
    resp.delete_cookie("intelli_session")
    return resp

