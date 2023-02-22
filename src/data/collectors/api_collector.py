from typing import Dict, Any, List, Optional
from enum import Enum
import json


class APIFormat(Enum):
    JSON = "json"
    XML = "xml"
    CSV = "csv"


class APICollector:
    def __init__(self, api_key: Optional[str] = None, base_url: str = ""):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None

    def fetch_properties(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        return []

    def fetch_single_property(self, property_id: str) -> Optional[Dict[str, Any]]:
        return None

    def fetch_market_data(
        self, emirate: str, data_type: str = "summary",
        start_date: Optional[str] = None, end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {}

    def fetch_transactions(
        self, date_from: str, date_to: str,
        emirate: Optional[str] = None, limit: int = 100,
    ) -> List[Dict[str, Any]]:
        return []

    def build_request(self, method: str, endpoint: str,
                      params: Optional[Dict] = None,
                      data: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return {
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
            "data": json.dumps(data) if data else None,
        }


class BatchCollector:
    def __init__(self, collectors: List[APICollector]):
        self.collectors = collectors

    def collect_all(self, parallel: bool = True) -> Dict[str, Any]:
        results = {"success": [], "failed": []}
        for collector in self.collectors:
            try:
                results["success"].append({"collector": str(collector), "count": 0})
            except Exception as e:
                results["failed"].append({"collector": str(collector), "error": str(e)})
        return results
