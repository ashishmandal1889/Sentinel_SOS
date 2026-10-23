"""
Sentinel SOS - Dispatch and Responder Matching Service.

Matches eligible emergency responders based on availability, emergency qualifications,
service area bounds, and proximity. Ensures concurrency control on assignments.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.models.sql.assignment import IncidentAssignment
from app.models.sql.responder import Responder
from app.repositories.responder_repository import ResponderRepository
from app.services.location_service import haversine_distance_meters


class DispatchService:
    def __init__(self, db: Session):
        self.db = db
        self.responder_repo = ResponderRepository(db)

    def find_eligible_responders(
        self,
        incident_lat: float,
        incident_lon: float,
        emergency_type: str = "GENERAL",
    ) -> List[dict]:
        """
        Finds active, verified responders whose service radius covers the incident.
        Uses Haversine distance as preliminary spatial filter.
        """
        available = self.responder_repo.get_available_responders(emergency_type)
        candidates = []

        for resp in available:
            if resp.current_latitude is None or resp.current_longitude is None:
                continue

            # Verify qualifications
            quals = [q.strip().upper() for q in resp.qualifications.split(",")]
            if "GENERAL" not in quals and emergency_type.upper() not in quals:
                continue

            dist_meters = haversine_distance_meters(
                incident_lat, incident_lon, resp.current_latitude, resp.current_longitude
            )
            dist_km = dist_meters / 1000.0

            if dist_km <= resp.service_radius_km:
                candidates.append({
                    "responder_id": resp.id,
                    "distance_meters": dist_meters,
                    "distance_km": round(dist_km, 2),
                    "badge_number": resp.badge_number,
                })

        # Sort by distance
        candidates.sort(key=lambda x: x["distance_meters"])
        return candidates

    def assign_responder(
        self,
        incident_id: str,
        responder_id: str,
        distance_meters: Optional[float] = None,
        eta_seconds: Optional[int] = None,
    ) -> IncidentAssignment:
        """
        Transactionally creates an assignment offer for a responder,
        preventing duplicate active assignments.
        """
        # Concurrency check: does an accepted assignment already exist?
        existing_accepted = (
            self.db.query(IncidentAssignment)
            .filter(
                IncidentAssignment.incident_id == incident_id,
                IncidentAssignment.status.in_(["ACCEPTED", "ARRIVED"]),
            )
            .first()
        )
        if existing_accepted:
            raise ValueError(f"Incident '{incident_id}' has already been assigned to another responder.")

        assignment = IncidentAssignment(
            incident_id=incident_id,
            responder_id=responder_id,
            status="OFFERED",
            distance_meters=distance_meters,
            eta_seconds=eta_seconds,
            offered_at=datetime.now(timezone.utc),
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
