"""
Sentinel SOS - Incident Service.

Handles retrieval of incident details, event history, and citizen incident logs.
"""

from typing import Any, Dict, List, Optional
from app.repositories.incident_repository import IncidentRepository


class IncidentService:
    def __init__(self, incident_repo: Optional[IncidentRepository] = None):
        self.incident_repo = incident_repo or IncidentRepository()

    def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        return self.incident_repo.get_incident(incident_id)

    def get_events(self, incident_id: str) -> List[Dict[str, Any]]:
        return self.incident_repo.get_events_by_incident(incident_id)
