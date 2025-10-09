# app/db/database.py
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is missing in .env")

engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    from app.db import models
    print("🧱 Creating database tables...")
    SQLModel.metadata.create_all(engine)

def get_session():
    """FastAPI dependency to get a database session."""
    with Session(engine) as session:
        yield session
