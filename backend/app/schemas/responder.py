"""
Sentinel SOS - Responder Schemas.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ResponderStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"


class ResponderRegisterRequest(BaseModel):
    badge_number: Optional[str] = None
    qualifications: str = Field(default="GENERAL", description="Comma separated qualified emergency types.")
    service_radius_km: float = Field(default=15.0, ge=1.0, le=100.0)


class ResponderLocationUpdate(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    status: Optional[ResponderStatus] = None


class ResponderResponse(BaseModel):
    id: str
    user_id: str
    badge_number: Optional[str]
    status: ResponderStatus
    is_verified: bool
    qualifications: str
    service_radius_km: float
    current_latitude: Optional[float]
    current_longitude: Optional[float]
    location_updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class AssignmentActionRequest(BaseModel):
    action: str = Field(..., description="'ACCEPT' or 'DECLINE'")
    note: Optional[str] = None
