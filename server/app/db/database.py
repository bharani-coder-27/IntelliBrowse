# app/db/database.py
from sqlmodel import SQLModel, create_engine, Session
import os

DB_PATH = os.path.join("data", "navigator.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

def init_db():
    """Create all tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Context-managed session"""
    with Session(engine) as session:
        yield session
