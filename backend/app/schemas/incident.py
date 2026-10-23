"""
Sentinel SOS - Emergency and Incident Schemas.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IncidentStatus(str, Enum):
    CREATED = "CREATED"
    NOTIFYING = "NOTIFYING"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    DISPATCHED = "DISPATCHED"
    ON_THE_WAY = "ON_THE_WAY"
    ARRIVED = "ARRIVED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"
    ESCALATED = "ESCALATED"
    NO_RESPONDER_AVAILABLE = "NO_RESPONDER_AVAILABLE"


class EmergencyType(str, Enum):
    MEDICAL = "MEDICAL"
    FIRE = "FIRE"
    POLICE = "POLICE"
    ACCIDENT = "ACCIDENT"
    GENERAL = "GENERAL"


class SOSCreateRequest(BaseModel):
    emergency_type: EmergencyType = Field(default=EmergencyType.GENERAL)
    latitude: float = Field(..., ge=-90.0, le=90.0, description="WGS84 latitude coordinate.")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="WGS84 longitude coordinate.")
    accuracy_meters: Optional[float] = Field(default=None, ge=0.0, description="GPS accuracy in meters.")
    description: Optional[str] = Field(default=None, max_length=1000)
    client_request_id: Optional[str] = Field(default=None, description="Idempotency key for duplicate protection.")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SOSCreateResponse(BaseModel):
    incident_id: str
    status: IncidentStatus
    created_at: datetime
    location_status: str
    message: str


class IncidentEventResponse(BaseModel):
    event_id: str
    incident_id: str
    event_type: str
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    note: Optional[str] = None
    timestamp: datetime


class IncidentStatusUpdateRequest(BaseModel):
    status: IncidentStatus
    note: Optional[str] = None


class IncidentDetailResponse(BaseModel):
    incident_id: str
    citizen_id: str
    emergency_type: EmergencyType
    status: IncidentStatus
    latitude: float
    longitude: float
    accuracy_meters: Optional[float] = None
    address: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    assigned_responder_id: Optional[str] = None
