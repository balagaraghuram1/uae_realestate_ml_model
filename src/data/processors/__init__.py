from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class PipelineStage:
    name: str
    processor: Callable
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class PipelineOrchestrator:
    def __init__(self):
        self.stages: List[PipelineStage] = []

    def add_stage(self, stage: PipelineStage) -> None:
        self.stages.append(stage)

    def insert_stage(self, index: int, stage: PipelineStage) -> None:
        self.stages.insert(index, stage)

    def remove_stage(self, name: str) -> bool:
        initial = len(self.stages)
        self.stages = [s for s in self.stages if s.name != name]
        return len(self.stages) < initial

    def execute(self, data: Any) -> Dict[str, Any]:
        pipeline_log = {"stages": [], "current": data}
        for stage in self.stages:
            if not stage.enabled:
                continue
            stage_log = {"name": stage.name, "input_shape": self._shape_of(pipeline_log["current"])}
            try:
                pipeline_log["current"] = stage.processor(pipeline_log["current"])
                stage_log["status"] = "success"
                stage_log["output_shape"] = self._shape_of(pipeline_log["current"])
            except Exception as e:
                stage_log["status"] = "failed"
                stage_log["error"] = str(e)
                pipeline_log["stages"].append(stage_log)
                break
            pipeline_log["stages"].append(stage_log)
        return pipeline_log

    @staticmethod
    def _shape_of(data: Any) -> str:
        if isinstance(data, list):
            return f"list[{len(data)}]"
        elif isinstance(data, dict):
            return f"dict[{len(data)} keys]"
        elif hasattr(data, "shape"):
            return str(data.shape)
        return str(type(data).__name__)

    def get_execution_plan(self) -> List[Dict[str, Any]]:
        return [
            {"name": s.name, "processor": s.processor.__name__, "enabled": s.enabled}
            for s in self.stages
        ]


class DataNormalizer:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def normalize_price(self, price: float) -> float:
        return abs(float(price))

    def normalize_size(self, size_sqft: float, target_unit: str = "sqft") -> float:
        conversions = {"sqft": 1.0, "sqm": 10.7639, "sqyd": 9.0}
        factor = conversions.get(target_unit, 1.0)
        return abs(float(size_sqft)) * (1.0 / factor)

    def normalize_coordinates(self, lat: float, lon: float) -> Dict[str, float]:
        return {"latitude": round(max(-90, min(90, float(lat))), 6), "longitude": round(max(-180, min(180, float(lon))), 6)}

    def normalize_emirate(self, value: str) -> str:
        mapping = {
            "dubai": "dubai", "dxb": "dubai",
            "abu dhabi": "abu_dhabi", "abudhabi": "abu_dhabi", "ad": "abu_dhabi",
            "sharjah": "sharjah", "shj": "sharjah",
            "ajman": "ajman",
            "ras al khaimah": "ras_al_khaimah", "rak": "ras_al_khaimah",
            "fujairah": "fujairah",
            "umm al quwain": "umm_al_quwain", "uaq": "umm_al_quwain",
        }
        return mapping.get(value.strip().lower(), value)

    def normalize_property_type(self, value: str) -> str:
        mapping = {
            "apartment": "apartment", "apt": "apartment", "flat": "apartment",
            "villa": "villa", "townhouse": "townhouse", "th": "townhouse",
            "penthouse": "penthouse", "ph": "penthouse",
            "commercial": "commercial", "office": "commercial", "shop": "commercial",
            "land": "land", "plot": "land",
        }
        return mapping.get(value.strip().lower(), value)


class DataEnricher:
    def __init__(self):
        self.enrichers: List[Callable] = []

    def register_enricher(self, enricher: Callable) -> None:
        self.enrichers.append(enricher)

    def enrich(self, record: Dict[str, Any]) -> Dict[str, Any]:
        enriched = dict(record)
        for enricher in self.enrichers:
            try:
                result = enricher(enriched)
                if isinstance(result, dict):
                    enriched.update(result)
            except Exception:
                continue
        return enriched

    def enrich_batch(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.enrich(r) for r in records]
