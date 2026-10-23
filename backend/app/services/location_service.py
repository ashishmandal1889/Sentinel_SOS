"""
Sentinel SOS - Location Service.

Provides geospatial calculations, Haversine straight-line distance filtering,
and coordinate boundary validations.
"""

import math
from typing import Tuple


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two GPS points in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def is_valid_coordinate(lat: float, lon: float) -> bool:
    """Validates WGS84 latitude and longitude boundaries."""
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0
