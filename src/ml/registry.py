import json
from typing import Dict, Any, Optional, List
from datetime import datetime


class ModelRegistry:
    def __init__(self, storage_path: str = "models/registry"):
        self.storage_path = storage_path
        self._models: Dict[str, Dict[str, Any]] = {}

    def register(self, model_id: str, model_type: str, version: str,
                 metrics: Optional[Dict[str, float]] = None,
                 tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        entry = {
            "model_id": model_id,
            "model_type": model_type,
            "version": version,
            "status": "registered",
            "metrics": metrics or {},
            "tags": tags or {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        key = f"{model_id}:{version}"
        self._models[key] = entry
        return entry

    def promote(self, model_id: str, version: str, stage: str = "production") -> bool:
        key = f"{model_id}:{version}"
        if key not in self._models:
            return False
        current_prod = self.get_stage(model_id, "production")
        if current_prod:
            self._models[current_prod["key"]]["status"] = "archived"
            self._models[current_prod["key"]]["stage"] = "archived"
        self._models[key]["status"] = stage
        self._models[key]["stage"] = stage
        self._models[key]["promoted_at"] = datetime.utcnow().isoformat()
        return True

    def get_stage(self, model_id: str, stage: str) -> Optional[Dict[str, Any]]:
        for key, entry in self._models.items():
            if entry.get("model_id") == model_id and entry.get("status") == stage:
                result = dict(entry)
                result["key"] = key
                return result
        return None

    def list_models(self, model_type: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        for entry in self._models.values():
            if model_type and entry.get("model_type") != model_type:
                continue
            results.append(entry)
        return results

    def get_model(self, model_id: str, version: str) -> Optional[Dict[str, Any]]:
        return self._models.get(f"{model_id}:{version}")

    def delete_model(self, model_id: str, version: str) -> bool:
        key = f"{model_id}:{version}"
        if key in self._models:
            del self._models[key]
            return True
        return False

    def get_latest(self, model_id: str) -> Optional[Dict[str, Any]]:
        candidates = []
        for key, entry in self._models.items():
            if entry.get("model_id") == model_id:
                candidates.append((key, entry))
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[1].get("created_at", ""), reverse=True)
        return candidates[0][1]

    def search(self, query: str) -> List[Dict[str, Any]]:
        query = query.lower()
        results = []
        for entry in self._models.values():
            if query in entry.get("model_id", "").lower() or \
               query in str(entry.get("tags", {})).lower() or \
               query in entry.get("model_type", "").lower():
                results.append(entry)
        return results
