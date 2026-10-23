"""
Sentinel SOS - Incident Repository (MongoDB).

Manages document storage for:
  - sos_incidents
  - sos_events
  - incident_snapshots

Includes resilient local fallback storage when MongoDB is not running (e.g. during local tests).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.core.logging import logger
from app.db.mongodb import get_mongo_db

# Resilient in-memory fallback store for offline tests
_FALLBACK_INCIDENTS: Dict[str, Dict[str, Any]] = {}
_FALLBACK_EVENTS: List[Dict[str, Any]] = []


class IncidentRepository:
    def __init__(self):
        self.db = get_mongo_db()

    def create_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        incident_id = incident_data["incident_id"]
        if self.db is not None:
            try:
                self.db["sos_incidents"].insert_one(incident_data.copy())
                return incident_data
            except Exception as e:
                logger.error(f"Failed to persist incident in MongoDB: {e}")

        # Fallback in-memory persistence
        _FALLBACK_INCIDENTS[incident_id] = incident_data.copy()
        return incident_data

    def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        if self.db is not None:
            try:
                doc = self.db["sos_incidents"].find_one({"incident_id": incident_id}, {"_id": 0})
                if doc:
                    return doc
            except Exception as e:
                logger.error(f"MongoDB read error: {e}")

        return _FALLBACK_INCIDENTS.get(incident_id)

    def update_incident_status(self, incident_id: str, new_status: str) -> bool:
        if self.db is not None:
            try:
                result = self.db["sos_incidents"].update_one(
                    {"incident_id": incident_id},
                    {"$set": {"status": new_status, "updated_at": datetime.now(timezone.utc)}},
                )
                if result.matched_count > 0:
                    return True
            except Exception as e:
                logger.error(f"MongoDB update error: {e}")

        if incident_id in _FALLBACK_INCIDENTS:
            _FALLBACK_INCIDENTS[incident_id]["status"] = new_status
            _FALLBACK_INCIDENTS[incident_id]["updated_at"] = datetime.now(timezone.utc)
            return True
        return False

    def add_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        if self.db is not None:
            try:
                self.db["sos_events"].insert_one(event_data.copy())
                return event_data
            except Exception as e:
                logger.error(f"MongoDB event insertion error: {e}")

        _FALLBACK_EVENTS.append(event_data.copy())
        return event_data

    def get_events_by_incident(self, incident_id: str) -> List[Dict[str, Any]]:
        if self.db is not None:
            try:
                cursor = self.db["sos_events"].find({"incident_id": incident_id}, {"_id": 0}).sort("timestamp", 1)
                return list(cursor)
            except Exception as e:
                logger.error(f"MongoDB events retrieval error: {e}")

        return [e for e in _FALLBACK_EVENTS if e.get("incident_id") == incident_id]
