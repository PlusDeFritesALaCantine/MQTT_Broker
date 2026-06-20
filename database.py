import os
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise ValueError("DB_URL is not set in environment variables")

engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autoflush=False, bind=engine)

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Database connected successfully.")
except Exception as e:
    print("Failed to connect to the database:", e)


class Base(DeclarativeBase):
    pass


def init_db():
    print("Création des tables si elles n'existent pas...")
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
