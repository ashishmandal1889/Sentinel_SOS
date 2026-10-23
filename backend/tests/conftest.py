"""
Sentinel SOS - Pytest Configuration & Test Fixtures.
"""

import os
import pytest
from fastapi.testclient import TestClient

# Set testing environment variables before importing settings
os.environ["SENTINEL_ENV"] = "testing"
os.environ["SQL_DATABASE_URL"] = "sqlite:///./sentinel_test.db"
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-that-is-at-least-32-characters-long!"
os.environ["SMS_PROVIDER"] = "mock"
os.environ["LLM_PROVIDER"] = "mock"

from app.main import app
from app.db.sql import Base, engine, SessionLocal
from app.core.security import create_access_token


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Initializes clean database schema for test session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./sentinel_test.db"):
        try:
            os.remove("./sentinel_test.db")
        except Exception:
            pass


@pytest.fixture
def client():
    """TestClient fixture with app."""
    return TestClient(app)


@pytest.fixture
def citizen_auth_headers():
    """Returns headers for an authenticated citizen user."""
    token = create_access_token(subject="user_citizen_123", role="citizen")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def responder_auth_headers():
    """Returns headers for an authenticated responder user."""
    token = create_access_token(subject="user_responder_456", role="responder")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers():
    """Returns headers for an authenticated admin user."""
    token = create_access_token(subject="user_admin_789", role="admin")
    return {"Authorization": f"Bearer {token}"}
