 """Geospatial utility functions for UAE property data."""
import math
from typing import Tuple, Dict

EARTH_RADIUS_KM = 6371.0

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points in km."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))

def find_nearby(lat: float, lon: float, radius_km: float, properties: list) -> list:
    """Find properties within a given radius."""
    nearby = []
    for prop in properties:
        if "latitude" in prop and "longitude" in prop:
            dist = haversine_distance(lat, lon, prop["latitude"], prop["longitude"])
            if dist <= radius_km:
                nearby.append({**prop, "distance_km": round(dist, 2)})
    return sorted(nearby, key=lambda x: x["distance_km"])

def get_bounding_box(lat: float, lon: float, radius_km: float) -> Dict[str, float]:
    """Get bounding box coordinates for a radius around a point."""
    lat_rad = math.radians(lat)
    delta_lat = radius_km / EARTH_RADIUS_KM * (180 / math.pi)
    delta_lon = delta_lat / math.cos(lat_rad)
    return {
        "min_lat": lat - delta_lat, "max_lat": lat + delta_lat,
        "min_lon": lon - delta_lon, "max_lon": lon + delta_lon,
    }
