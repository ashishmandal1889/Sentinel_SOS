"""
Sentinel SOS - Health & Readiness Diagnostics Endpoint.

Provides health and readiness checks for container orchestrators and monitoring tools,
reporting database connectivity and application status.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, status
from app.core.config import settings
from app.db.sql import check_sql_connection
from app.db.mongodb import check_mongo_connection

router = APIRouter()
START_TIME = datetime.now(timezone.utc)


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Basic liveness probe."""
    return {
        "status": "ok",
        "app_name": settings.SENTINEL_APP_NAME,
        "environment": settings.SENTINEL_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/readiness", status_code=status.HTTP_200_OK)
def readiness_check():
    """Detailed readiness probe including SQL and MongoDB connections."""
    sql_ok = check_sql_connection()
    mongo_ok = check_mongo_connection()

    overall_status = "ready" if sql_ok else "degraded"
    uptime_seconds = (datetime.now(timezone.utc) - START_TIME).total_seconds()

    return {
        "status": overall_status,
        "uptime_seconds": round(uptime_seconds, 2),
        "checks": {
            "sql_database": "connected" if sql_ok else "unreachable",
            "mongo_database": "connected" if mongo_ok else "unreachable/offline",
        },
        "version": "1.0.0",
        "environment": settings.SENTINEL_ENV,
    }
