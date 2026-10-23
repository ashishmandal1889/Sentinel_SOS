"""
Sentinel SOS - Configuration Namespace Tests.
"""

import pytest
from app.core.config import Settings


def test_settings_namespaces():
    settings = Settings()
    assert settings.SENTINEL_APP_NAME != ""
    assert settings.SENTINEL_API_PREFIX == "/api/v1"
    assert settings.SQL_DATABASE_URL != ""
    assert settings.MONGO_DATABASE != ""
    assert settings.SMS_PROVIDER in ["mock", "twilio", "msg91"]
    assert settings.LLM_PROVIDER in ["mock", "openai", "gemini"]


def test_production_secret_key_validation():
    with pytest.raises(ValueError, match="AUTH_SECRET_KEY"):
        Settings(
            SENTINEL_ENV="production",
            AUTH_SECRET_KEY="short-insecure-key",
            SQL_DATABASE_URL="postgresql://user:pass@localhost:5432/db",
        )


def test_production_sqlite_rejected():
    with pytest.raises(ValueError, match="SQLite is not supported for production"):
        Settings(
            SENTINEL_ENV="production",
            AUTH_SECRET_KEY="a-very-long-and-secure-random-key-for-sentinel-production-32-chars",
            SQL_DATABASE_URL="sqlite:///./prod.db",
        )
