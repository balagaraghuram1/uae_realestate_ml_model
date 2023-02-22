from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class ValidationRule:
    field: str
    rule_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    severity: str = "error"
    message: Optional[str] = None


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    field_errors: Dict[str, List[str]] = field(default_factory=dict)


class SchemaValidator:
    def __init__(self):
        self.rules: List[ValidationRule] = []

    def add_rule(self, rule: ValidationRule) -> None:
        self.rules.append(rule)

    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult(valid=True)
        for rule in self.rules:
            field_value = record.get(rule.field)
            field_result = self._apply_rule(rule, field_value, record)
            if rule.severity == "error" and not field_result:
                result.valid = False
                result.errors.append(rule.message or f"Validation failed on {rule.field}")
                if rule.field not in result.field_errors:
                    result.field_errors[rule.field] = []
                result.field_errors[rule.field].append(rule.message or f"Validation failed")
            elif rule.severity == "warning" and not field_result:
                result.warnings.append(rule.message or f"Warning on {rule.field}")
        return result

    def _apply_rule(self, rule: ValidationRule, value: Any, record: Dict[str, Any]) -> bool:
        if rule.rule_type == "required":
            return value is not None and value != ""
        elif rule.rule_type == "type":
            expected = rule.params.get("type")
            return isinstance(value, self._parse_type(expected)) if value is not None else True
        elif rule.rule_type == "range":
            min_val = rule.params.get("min")
            max_val = rule.params.get("max")
            if value is None:
                return True
            if min_val is not None and value < min_val:
                return False
            if max_val is not None and value > max_val:
                return False
            return True
        elif rule.rule_type == "regex":
            import re
            pattern = rule.params.get("pattern", "")
            if value is None:
                return True
            return bool(re.match(pattern, str(value)))
        elif rule.rule_type == "in_enum":
            allowed = rule.params.get("values", [])
            if value is None:
                return True
            return value in allowed
        elif rule.rule_type == "conditional_required":
            condition_field = rule.params.get("condition_field")
            condition_value = rule.params.get("condition_value")
            if record.get(condition_field) == condition_value:
                return value is not None and value != ""
            return True
        return True

    @staticmethod
    def _parse_type(type_str: str) -> type:
        mapping = {
            "str": str, "string": str,
            "int": int, "integer": int,
            "float": float, "double": float,
            "bool": bool, "boolean": bool,
            "list": list, "dict": dict,
            "NoneType": type(None),
        }
        return mapping.get(type_str.lower(), str)
