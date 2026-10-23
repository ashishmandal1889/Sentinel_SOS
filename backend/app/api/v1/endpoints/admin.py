"""
Sentinel SOS - Administrator Control Center Endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import AuthenticatedUser, require_roles
from app.db.sql import get_db
from app.models.sql.assignment import AuditLog
from app.models.sql.responder import Responder
from app.models.sql.user import User

router = APIRouter()


@router.get("/dashboard")
def get_admin_dashboard_stats(
    current_user: AuthenticatedUser = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db),
):
    """Provides real-time system metrics for the administrative dashboard."""
    total_users = db.query(User).count()
    total_responders = db.query(Responder).count()
    active_responders = db.query(Responder).filter(Responder.status == "AVAILABLE").count()

    return {
        "status": "operational",
        "total_users": total_users,
        "total_responders": total_responders,
        "active_responders": active_responders,
    }


@router.get("/audit-logs")
def get_audit_logs(
    limit: int = 50,
    current_user: AuthenticatedUser = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db),
):
    """Retrieves security and operational audit trail logs."""
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [{"id": l.id, "action": l.action, "user_id": l.user_id, "created_at": l.created_at} for l in logs]
