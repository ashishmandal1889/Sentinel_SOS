"""
Sentinel SOS - Relational Database Connection (PostgreSQL / SQLite).

Configures SQLAlchemy 2.0 engine, declarative base, and session generator.
"""

from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger

connect_args = {}
if "sqlite" in settings.SQL_DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.SQL_DATABASE_URL,
    echo=settings.SQL_ECHO,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields an active database session and ensures cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_sql_connection() -> bool:
    """Verifies relational database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"SQL Database connection check failed: {e}")
        return False
