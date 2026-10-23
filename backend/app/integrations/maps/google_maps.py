"""
Sentinel SOS - Google Maps Platform Integration Adapter.

Provides:
  - Reverse geocoding (coordinates to human-readable address)
  - Driving route and ETA calculation via Directions/Routes API
  - Nearby emergency facilities (Hospitals, Police stations) via Places API

Gracefully degrades to mock estimation when MAPS_GOOGLE_API_KEY is not configured.
"""

from typing import Any, Dict, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.services.location_service import haversine_distance_meters


class GoogleMapsClient:
    def __init__(self):
        self.api_key = settings.MAPS_GOOGLE_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 0)

    async def reverse_geocode(self, lat: float, lon: float) -> str:
        """Translates GPS coordinates into a formatted street address."""
        if not self.is_configured:
            logger.info("Google Maps API key not configured. Returning estimated coordinate label.")
            return f"Near Latitude: {lat:.4f}, Longitude: {lon:.4f}"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    f"{self.base_url}/geocode/json",
                    params={"latlng": f"{lat},{lon}", "key": self.api_key},
                )
                data = res.json()
                if data.get("status") == "OK" and data.get("results"):
                    return data["results"][0]["formatted_address"]
        except Exception as e:
            logger.error(f"Google Maps Geocoding failed: {e}")

        return f"Coordinates: ({lat}, {lon})"

    async def calculate_eta(
        self, origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float
    ) -> Dict[str, Any]:
        """Calculates driving distance and travel duration."""
        if not self.is_configured:
            # Fallback estimation using average emergency response vehicle speed (45 km/h)
            dist_meters = haversine_distance_meters(origin_lat, origin_lon, dest_lat, dest_lon)
            speed_mps = 12.5  # ~45 km/h
            est_seconds = int(dist_meters / speed_mps) + 60
            return {
                "distance_meters": round(dist_meters, 1),
                "duration_seconds": est_seconds,
                "is_estimated": True,
            }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    f"{self.base_url}/directions/json",
                    params={
                        "origin": f"{origin_lat},{origin_lon}",
                        "destination": f"{dest_lat},{dest_lon}",
                        "mode": "driving",
                        "key": self.api_key,
                    },
                )
                data = res.json()
                if data.get("status") == "OK" and data.get("routes"):
                    leg = data["routes"][0]["legs"][0]
                    return {
                        "distance_meters": leg["distance"]["value"],
                        "duration_seconds": leg["duration"]["value"],
                        "is_estimated": False,
                    }
        except Exception as e:
            logger.error(f"Google Directions API failure: {e}")

        dist_meters = haversine_distance_meters(origin_lat, origin_lon, dest_lat, dest_lon)
        return {
            "distance_meters": dist_meters,
            "duration_seconds": int(dist_meters / 12.5),
            "is_estimated": True,
        }


google_maps_client = GoogleMapsClient()
