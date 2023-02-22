from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum


class SourceType(Enum):
    API = "api"
    SCRAPER = "scraper"
    FILE = "file"
    DATABASE = "database"
    STREAM = "stream"


@dataclass
class DataSource:
    name: str
    source_type: SourceType
    config: Dict[str, Any]
    enabled: bool = True
    priority: int = 0
    schedule: Optional[str] = None


class Orchestrator:
    def __init__(self):
        self.sources: List[DataSource] = []
        self.pipeline = DataPipeline()

    def register_source(self, source: DataSource) -> None:
        self.sources.append(source)
        self.sources.sort(key=lambda s: s.priority)

    def run_collection(self, source_name: Optional[str] = None) -> Dict[str, Any]:
        results = {"collected": 0, "failed": 0, "errors": []}
        targets = [s for s in self.sources if s.name == source_name] if source_name else self.sources
        for source in targets:
            if not source.enabled:
                continue
            try:
                records = self._collect_from_source(source)
                processed = self.pipeline.process(records)
                results["collected"] += len(processed)
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"{source.name}: {str(e)}")
        return results

    def _collect_from_source(self, source: DataSource) -> List[Dict[str, Any]]:
        return []


class DataPipeline:
    def __init__(self):
        self.transformers = []
        self.validators = []

    def add_transformer(self, transformer) -> None:
        self.transformers.append(transformer)

    def add_validator(self, validator) -> None:
        self.validators.append(validator)

    def process(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result = records
        for transformer in self.transformers:
            result = transformer.transform(result)
        for validator in self.validators:
            result = [r for r in result if validator.validate(r)]
        return result
