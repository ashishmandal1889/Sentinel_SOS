"""
Sentinel SOS - Background Notification Worker.

Handles asynchronous background notification tasks, retries, and delivery tracking.
Can be dispatched directly via FastAPI BackgroundTasks or connected to a Celery worker.
"""

from typing import Dict, Any
from app.core.logging import logger
from app.services.notification_service import NotificationService


async def process_notification_job(payload: Dict[str, Any]) -> None:
    """Processes background notification dispatch."""
    service = NotificationService()
    logger.info(f"Processing background notification job for incident {payload.get('incident_id')}")
    service.send_sos_alert(
        incident_id=payload.get("incident_id", "unknown"),
        recipient_phone=payload.get("phone", ""),
        citizen_name=payload.get("citizen_name", "Citizen"),
        location_url=payload.get("location_url", "https://maps.google.com"),
    )
