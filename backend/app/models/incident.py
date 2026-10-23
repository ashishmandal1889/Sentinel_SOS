"""
Sentinel SOS - MongoDB Incident Document Representation.

Defines the document structure for records stored in MongoDB collections:
  - 'sos_incidents'
  - 'sos_events'
  - 'responder_location_history'
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.incident import EmergencyType, IncidentStatus


class SOSIncidentDocument(BaseModel):
    incident_id: str
    citizen_id: str
    emergency_type: EmergencyType
    status: IncidentStatus
    latitude: float
    longitude: float
    accuracy_meters: Optional[float] = None
    address: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    assigned_responder_id: Optional[str] = None
