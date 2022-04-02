"""Geocoding service for UAE property addresses."""
import time, logging, requests
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class Geocoder:
    """Convert UAE property addresses to latitude/longitude coordinates."""

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    RATE_LIMIT = 1.1

    def __init__(self):
        self._last_request = 0

    def geocode(self, address: str, emirate: str = "Dubai") -> Optional[Tuple[float, float]]:
        """Geocode an address to coordinates."""
        time.sleep(max(0, self.RATE_LIMIT - (time.time() - self._last_request)))
        query = f"{address}, {emirate}, UAE"
        try:
            resp = requests.get(self.NOMINATIM_URL, params={
                "q": query, "format": "json", "limit": 1,
                "countrycodes": "ae",
            }, timeout=10, headers={"User-Agent": "UAE-RealEstate-ML/1.0"})
            self._last_request = time.time()
            if resp.status_code == 200 and resp.json():
                data = resp.json()[0]
                return float(data["lat"]), float(data["lon"])
        except Exception as e:
            logger.warning("Geocoding failed for %s: %s", query, e)
        return None

    def batch_geocode(self, addresses: list) -> list:
        """Geocode a batch of addresses."""
        results = []
        for addr in addresses:
            coords = self.geocode(addr.get("address", ""), addr.get("emirate", "Dubai"))
            results.append({
                **addr,
                "latitude": coords[0] if coords else None,
                "longitude": coords[1] if coords else None,
            })
        return results
