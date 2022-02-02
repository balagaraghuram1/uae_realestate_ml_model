"""ML Model Registry with versioning, metadata tracking, and artifact storage."""
import os, json, hashlib, shutil, logging
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ModelVersion:
    """Metadata for a single model version."""
    model_name: str
    version: int
    artifact_path: str
    metrics: Dict[str, float] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "active"
    description: str = ""

class ModelRegistry:
    """Central registry for ML model versioning and metadata."""

    def __init__(self, registry_dir: str = "model_registry"):
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = self.registry_dir / "index.json"
        self._index = self._load_index()

    def _load_index(self) -> Dict:
        if self._index_file.exists():
            with open(self._index_file, "r") as f:
                return json.load(f)
        return {"models": {}}

    def _save_index(self):
        with open(self._index_file, "w") as f:
            json.dump(self._index, f, indent=2)

    def register_model(self, model_name: str, artifact_path: str,
                       metrics: Dict = None, parameters: Dict = None,
                       description: str = "") -> ModelVersion:
        """Register a new model version."""
        if model_name not in self._index["models"]:
            self._index["models"][model_name] = {"versions": [], "latest_version": 0}
        latest = self._index["models"][model_name]["latest_version"]
        new_version = latest + 1
        version_dir = self.registry_dir / model_name / f"v{new_version}"
        version_dir.mkdir(parents=True, exist_ok=True)
        dest_artifact = version_dir / "model.pkl"
        shutil.copy2(artifact_path, dest_artifact)
        checksum = hashlib.md5(open(dest_artifact, "rb").read()).hexdigest()
        mv = ModelVersion(
            model_name=model_name, version=new_version,
            artifact_path=str(dest_artifact), metrics=metrics or {},
            parameters=parameters or {}, description=description,
            tags={"checksum": checksum},
        )
        metadata_file = version_dir / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(mv.__dict__, f, indent=2)
        self._index["models"][model_name]["versions"].append(new_version)
        self._index["models"][model_name]["latest_version"] = new_version
        self._save_index()
        logger.info("Registered %s v%d", model_name, new_version)
        return mv

    def load_model(self, model_name: str, version: Optional[int] = None):
        """Load a model artifact from the registry."""
        if version is None:
            version = self._index["models"][model_name]["latest_version"]
        path = self.registry_dir / model_name / f"v{version}" / "model.pkl"
        if not path.exists():
            raise FileNotFoundError(f"Model artifact not found: {path}")
        import joblib
        return joblib.load(str(path))

    def list_models(self) -> Dict[str, Dict]:
        """List all registered models."""
        return self._index["models"]

    def promote_model(self, model_name: str, version: int, stage: str):
        """Promote a model version to a different stage."""
        meta_path = self.registry_dir / model_name / f"v{version}" / "metadata.json"
        if meta_path.exists():
            with open(meta_path) as f:
                meta = json.load(f)
            meta["status"] = stage
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=2)
            logger.info("Promoted %s v%d to %s", model_name, version, stage)

    def compare_versions(self, model_name: str, v1: int, v2: int) -> Dict:
        """Compare metrics between two model versions."""
        result = {}
        for ver in [v1, v2]:
            meta_path = self.registry_dir / model_name / f"v{ver}" / "metadata.json"
            if meta_path.exists():
                with open(meta_path) as f:
                    result[f"v{ver}"] = json.load(f)
        return result
