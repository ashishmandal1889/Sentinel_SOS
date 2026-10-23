"""
Sentinel SOS - Centralized Configuration Module.

Loads and validates environment variables using Pydantic Settings v2.
Organized into consistent namespaces:
  - SENTINEL_* : Core application settings
  - SQL_*      : Relational database (PostgreSQL / SQLite for dev/test)
  - MONGO_*    : Document database (MongoDB)
  - AUTH_*     : Authentication and JWT
  - MAPS_*     : Google Maps Platform
  - SMS_*      : SMS provider (Mock / Twilio / MSG91)
  - PUSH_*     : Push notification provider (Firebase Cloud Messaging)
  - LLM_*      : Emergency Classification LLM (Mock / Gemini / OpenAI)
"""

from typing import List, Literal, Optional
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # --------------------------------------------------------------------------
    # Application Namespace (SENTINEL_*)
    # --------------------------------------------------------------------------
    SENTINEL_APP_NAME: str = Field(
        default="Sentinel SOS Emergency Response API",
        description="Application name displayed in OpenAPI docs and system metadata.",
    )
    SENTINEL_ENV: Literal["development", "testing", "staging", "production"] = Field(
        default="development",
        description="Deployment environment profile.",
    )
    SENTINEL_API_PREFIX: str = Field(
        default="/api/v1",
        description="Global API route prefix.",
    )
    SENTINEL_DEBUG: bool = Field(
        default=False,
        description="Enables verbose logging and debug utilities.",
    )
    SENTINEL_ALLOWED_ORIGINS: List[str] = Field(
        default=["*"],
        description="List of allowed CORS origins.",
    )

    # --------------------------------------------------------------------------
    # Relational Database Namespace (SQL_*)
    # --------------------------------------------------------------------------
    SQL_DATABASE_URL: str = Field(
        default="sqlite:///./sentinel_dev.db",
        description="PostgreSQL or SQLite database connection URI.",
    )
    SQL_ECHO: bool = Field(
        default=False,
        description="Log all generated SQL statements when True.",
    )

    # --------------------------------------------------------------------------
    # Document Database Namespace (MONGO_*)
    # --------------------------------------------------------------------------
    MONGO_URI: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI.",
    )
    MONGO_DATABASE: str = Field(
        default="sentinel_sos",
        description="Target MongoDB database name for emergency events.",
    )

    # --------------------------------------------------------------------------
    # Authentication Namespace (AUTH_*)
    # --------------------------------------------------------------------------
    AUTH_SECRET_KEY: str = Field(
        default="insecure-dev-secret-key-please-replace-in-production-min-32-chars",
        description="Cryptographic secret key for signing JWT tokens.",
    )
    AUTH_ALGORITHM: str = Field(
        default="HS256",
        description="JWT signature algorithm.",
    )
    AUTH_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60,
        ge=5,
        description="JWT token validity duration in minutes.",
    )

    # --------------------------------------------------------------------------
    # Google Maps Platform Namespace (MAPS_*)
    # --------------------------------------------------------------------------
    MAPS_GOOGLE_API_KEY: Optional[str] = Field(
        default=None,
        description="Google Maps API Key for Geocoding and Directions/Routes.",
    )

    # --------------------------------------------------------------------------
    # SMS Provider Namespace (SMS_*)
    # --------------------------------------------------------------------------
    SMS_PROVIDER: Literal["mock", "twilio", "msg91"] = Field(
        default="mock",
        description="Active SMS adapter. Defaults to mock for zero-credential dev/tests.",
    )
    SMS_MSG91_API_KEY: Optional[str] = Field(
        default=None,
        description="MSG91 authentication key.",
    )
    SMS_TWILIO_ACCOUNT_SID: Optional[str] = Field(
        default=None,
        description="Twilio Account SID (starts with AC).",
    )
    SMS_TWILIO_AUTH_TOKEN: Optional[str] = Field(
        default=None,
        description="Twilio Auth Token.",
    )
    SMS_TWILIO_API_KEY_SID: Optional[str] = Field(
        default=None,
        description="Twilio API Key SID (starts with SK).",
    )
    SMS_TWILIO_API_KEY_SECRET: Optional[str] = Field(
        default=None,
        description="Twilio API Key Secret.",
    )
    SMS_TWILIO_FROM_NUMBER: Optional[str] = Field(
        default=None,
        description="Twilio origin phone number.",
    )

    # --------------------------------------------------------------------------
    # Push Notifications Namespace (PUSH_*)
    # --------------------------------------------------------------------------
    PUSH_FCM_PROJECT_ID: Optional[str] = Field(
        default=None,
        description="Firebase Cloud Messaging Project ID.",
    )
    PUSH_CREDENTIALS_PATH: Optional[str] = Field(
        default=None,
        description="Path to service-account JSON credentials for Firebase.",
    )

    # --------------------------------------------------------------------------
    # LLM Provider Namespace (LLM_*)
    # --------------------------------------------------------------------------
    LLM_PROVIDER: Literal["mock", "openai", "gemini"] = Field(
        default="mock",
        description="Active LLM adapter for emergency triage classification.",
    )
    LLM_API_KEY: Optional[str] = Field(
        default=None,
        description="API key for selected LLM provider.",
    )
    LLM_MODEL: str = Field(
        default="gemini-1.5-flash",
        description="Model identifier for triage classification.",
    )

    # --------------------------------------------------------------------------
    # Email Provider Namespace (RESEND_*)
    # --------------------------------------------------------------------------
    RESEND_API_KEY: Optional[str] = Field(
        default=None,
        description="Resend API Key for dispatching email notifications.",
    )
    RESEND_FROM_EMAIL: str = Field(
        default="Sentinel SOS <onboarding@resend.dev>",
        description="Default sender email address for Resend.",
    )

    # --------------------------------------------------------------------------
    # Validators & Startup Verification
    # --------------------------------------------------------------------------
    @model_validator(mode="after")
    def validate_production_configuration(self) -> "Settings":
        """
        Validate critical security and credentials without exposing secret values.
        """
        if self.SENTINEL_ENV == "production":
            if (
                "insecure" in self.AUTH_SECRET_KEY
                or len(self.AUTH_SECRET_KEY) < 32
            ):
                raise ValueError(
                    "Production configuration error: AUTH_SECRET_KEY must be a cryptographically strong secret of at least 32 characters."
                )

            if "sqlite" in self.SQL_DATABASE_URL.lower():
                raise ValueError(
                    "Production configuration error: SQLite is not supported for production. Use PostgreSQL via SQL_DATABASE_URL."
                )

        # Validate SMS provider credentials only when that provider is enabled
        if self.SMS_PROVIDER == "twilio":
            has_auth_token = bool(self.SMS_TWILIO_ACCOUNT_SID and self.SMS_TWILIO_AUTH_TOKEN)
            has_api_key = bool(self.SMS_TWILIO_ACCOUNT_SID and self.SMS_TWILIO_API_KEY_SID and self.SMS_TWILIO_API_KEY_SECRET)
            if not (has_auth_token or has_api_key):
                raise ValueError(
                    "SMS configuration error: Twilio requires SMS_TWILIO_ACCOUNT_SID and either SMS_TWILIO_AUTH_TOKEN or (SMS_TWILIO_API_KEY_SID and SMS_TWILIO_API_KEY_SECRET)."
                )
        elif self.SMS_PROVIDER == "msg91":
            if not self.SMS_MSG91_API_KEY:
                raise ValueError(
                    "SMS configuration error: SMS_MSG91_API_KEY is required when SMS_PROVIDER is 'msg91'."
                )

        # Validate LLM credentials only when active provider is not mock
        if self.LLM_PROVIDER in ("openai", "gemini"):
            if not self.LLM_API_KEY:
                raise ValueError(
                    f"LLM configuration error: LLM_API_KEY is required when LLM_PROVIDER is '{self.LLM_PROVIDER}'."
                )

        return self

    @property
    def is_testing(self) -> bool:
        return self.SENTINEL_ENV == "testing"

    @property
    def is_development(self) -> bool:
        return self.SENTINEL_ENV == "development"


# Singleton instance loaded once at application import
settings = Settings()
