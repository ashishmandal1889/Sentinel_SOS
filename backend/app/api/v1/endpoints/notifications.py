"""
Sentinel SOS - Notification Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends
from app.core.dependencies import AuthenticatedUser, require_roles
from app.services.notification_service import NotificationService

router = APIRouter()


@router.post("/test")
def send_test_notification(
    phone_number: str,
    current_user: AuthenticatedUser = Depends(require_roles(["admin"])),
):
    """Sends a test emergency dispatch SMS/push message."""
    service = NotificationService()
    result = service.send_sos_alert(
        incident_id="test_incident",
        recipient_phone=phone_number,
        citizen_name="System Admin",
        location_url="https://maps.google.com/?q=0,0",
    )
    return {"message": "Test notification executed.", "details": result}


@router.post("/test-email")
async def send_test_email(
    email: str,
    current_user: AuthenticatedUser = Depends(require_roles(["admin"])),
):
    """Sends a test emergency dispatch email via Resend."""
    service = NotificationService()
    result = await service.send_sos_email(
        incident_id="test_incident_email",
        recipient_email=email,
        citizen_name="System Admin",
        location_url="https://maps.google.com/?q=0,0",
        emergency_type="TEST_ALERT",
    )
    return {"message": "Test email executed.", "details": result}


@router.post("/test-push")
async def send_test_push(
    fcm_token: str,
    title: str = "🚨 Sentinel SOS Emergency Test",
    body: str = "This is a test emergency push notification from Sentinel SOS.",
    current_user: AuthenticatedUser = Depends(require_roles(["admin"])),
):
    """Sends a test emergency push notification via Firebase Cloud Messaging."""
    service = NotificationService()
    result = await service.send_sos_push(
        incident_id="test_incident_push",
        fcm_token=fcm_token,
        title=title,
        body=body,
    )
    return {"message": "Test push notification executed.", "details": result}
