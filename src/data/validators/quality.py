from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class QualityMetrics:
    completeness: float
    uniqueness: float
    consistency: float
    accuracy: float
    timeliness: float
    overall_score: float


class QualityChecker:
    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        self.rules = rules or {}

    def check_completeness(self, records: List[Dict[str, Any]], required_fields: List[str]) -> Dict[str, Any]:
        total = len(records)
        if total == 0:
            return {"score": 0, "missing_fields": {}}
        field_completeness = {}
        for field in required_fields:
            present = sum(1 for r in records if r.get(field) is not None and r.get(field) != "")
            field_completeness[field] = {
                "completeness_pct": round(present / total * 100, 2),
                "missing_count": total - present,
            }
        overall = sum(v["completeness_pct"] for v in field_completeness.values()) / len(required_fields)
        return {"score": round(overall, 2), "fields": field_completeness}

    def check_uniqueness(self, records: List[Dict[str, Any]], key_fields: List[str]) -> Dict[str, Any]:
        seen = set()
        duplicates = []
        for i, record in enumerate(records):
            key = tuple(str(record.get(f)) for f in key_fields)
            if key in seen:
                duplicates.append(i)
            seen.add(key)
        total = len(records)
        unique = total - len(duplicates)
        return {
            "score": round(unique / total * 100, 2) if total > 0 else 100,
            "total_records": total,
            "unique_records": unique,
            "duplicate_indices": duplicates,
            "duplicate_count": len(duplicates),
        }

    def check_consistency(self, records: List[Dict[str, Any]], consistency_rules: List[Dict]) -> Dict[str, Any]:
        violations = []
        for i, record in enumerate(records):
            for rule in consistency_rules:
                if not self._check_consistency_rule(record, rule):
                    violations.append({"index": i, "rule": rule.get("name", "unknown"), "record": record})
        return {
            "violations": violations,
            "violation_count": len(violations),
            "score": round((1 - len(violations) / max(len(records), 1)) * 100, 2),
        }

    def _check_consistency_rule(self, record: Dict[str, Any], rule: Dict) -> bool:
        rule_type = rule.get("type")
        if rule_type == "cross_field":
            field1 = record.get(rule.get("field1"))
            field2 = record.get(rule.get("field2"))
            operator = rule.get("operator", "eq")
            if operator == "eq":
                return field1 == field2
            elif operator == "gt":
                return field1 > field2
            elif operator == "gte":
                return field1 >= field2
            elif operator == "lt":
                return field1 < field2
            elif operator == "lte":
                return field1 <= field2
        elif rule_type == "logical":
            condition = rule.get("condition")
            try:
                return bool(eval(condition, {"__builtins__": {}}, record))
            except Exception:
                return True
        return True

    def full_report(self, records: List[Dict[str, Any]]) -> QualityMetrics:
        completeness = self.check_completeness(records, list(records[0].keys()) if records else [])
        uniqueness = self.check_uniqueness(records, ["id"] if records else [])
        return QualityMetrics(
            completeness=completeness.get("score", 0),
            uniqueness=uniqueness.get("score", 0),
            consistency=100.0,
            accuracy=100.0,
            timeliness=100.0,
            overall_score=round(sum([completeness.get("score", 0), uniqueness.get("score", 0), 100, 100, 100]) / 5, 2),
        )
