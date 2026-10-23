"""
Sentinel SOS - Notification Schemas.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel


class NotificationDispatchPayload(BaseModel):
    recipient_id: str
    channel: str  # "sms", "push", "email"
    destination: str  # phone number, FCM token, or email
    title: str
    body: str
    metadata: Optional[Dict[str, Any]] = None


class NotificationRecordResponse(BaseModel):
    id: str
    incident_id: str
    channel: str
    destination: str
    status: str  # SUBMITTED, DELIVERED, FAILED
    error_message: Optional[str] = None
    created_at: datetime
