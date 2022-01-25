"""Data validation using custom schema rules."""
import logging
import pandas as pd
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ValidationResult:
    """Result of a single validation check."""
    rule_name: str
    passed: bool
    severity: Severity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationReport:
    """Complete validation report."""
    results: List[ValidationResult] = field(default_factory=list)
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0

    @property
    def is_valid(self) -> bool:
        return not any(r.severity == Severity.CRITICAL and not r.passed for r in self.results)

    def summary(self) -> Dict[str, Any]:
        return {
            "total_checks": self.total_checks,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "is_valid": self.is_valid,
        }


class SchemaValidator:
    """Validate DataFrames against defined schemas and business rules."""

    def __init__(self):
        self.rules: List[Dict[str, Any]] = []
        self._custom_checks: List[Callable] = []

    def add_not_null(self, columns: List[str], severity: Severity = Severity.ERROR):
        """Add not-null constraint for columns."""
        for col in columns:
            self.rules.append({
                "type": "not_null", "column": col, "severity": severity,
            })

    def add_range(self, column: str, min_val: Any = None, max_val: Any = None,
                  severity: Severity = Severity.ERROR):
        """Add range constraint for numeric columns."""
        self.rules.append({
            "type": "range", "column": column,
            "min": min_val, "max": max_val, "severity": severity,
        })

    def add_allowed_values(self, column: str, values: List[Any],
                           severity: Severity = Severity.WARNING):
        """Add enum constraint."""
        self.rules.append({
            "type": "allowed_values", "column": column,
            "values": values, "severity": severity,
        })

    def add_uniqueness(self, columns: List[str], severity: Severity = Severity.ERROR):
        """Add uniqueness constraint."""
        self.rules.append({
            "type": "uniqueness", "columns": columns, "severity": severity,
        })

    def add_custom(self, check_fn: Callable, name: str,
                   severity: Severity = Severity.WARNING):
        """Add a custom validation function."""
        self._custom_checks.append({"fn": check_fn, "name": name, "severity": severity})

    def validate(self, df: pd.DataFrame) -> ValidationReport:
        """Run all validation rules against the DataFrame."""
        report = ValidationReport()
        for rule in self.rules:
            result = self._apply_rule(df, rule)
            report.results.append(result)
            report.total_checks += 1
            if result.passed:
                report.passed += 1
            else:
                report.failed += 1
                if result.severity == Severity.WARNING:
                    report.warnings += 1
        for check in self._custom_checks:
            try:
                passed = check["fn"](df)
                result = ValidationResult(
                    rule_name=check["name"], passed=passed,
                    severity=check["severity"],
                    message=f"Custom check {'passed' if passed else 'failed'}",
                )
            except Exception as e:
                result = ValidationResult(
                    rule_name=check["name"], passed=False,
                    severity=check["severity"],
                    message=f"Custom check error: {e}",
                )
            report.results.append(result)
            report.total_checks += 1
            if result.passed:
                report.passed += 1
            else:
                report.failed += 1
        logger.info("Validation complete: %d/%d passed", report.passed, report.total_checks)
        return report

    def _apply_rule(self, df: pd.DataFrame, rule: Dict) -> ValidationResult:
        """Apply a single validation rule."""
        rule_type = rule["type"]
        severity = rule["severity"]
        column = rule.get("column", "")
        if rule_type == "not_null":
            if column not in df.columns:
                return ValidationResult(
                    rule_name=f"not_null({column})", passed=False,
                    severity=severity, message=f"Column '{column}' not found",
                )
            null_count = df[column].isna().sum()
            passed = null_count == 0
            return ValidationResult(
                rule_name=f"not_null({column})", passed=passed,
                severity=severity,
                message=f"Column '{column}' has {null_count} null values" if not passed else "OK",
                details={"null_count": int(null_count)},
            )
        elif rule_type == "range":
            if column not in df.columns:
                return ValidationResult(
                    rule_name=f"range({column})", passed=False,
                    severity=severity, message=f"Column '{column}' not found",
                )
            numeric = pd.to_numeric(df[column], errors="coerce")
            violations = 0
            if rule.get("min") is not None:
                violations += (numeric < rule["min"]).sum()
            if rule.get("max") is not None:
                violations += (numeric > rule["max"]).sum()
            passed = violations == 0
            return ValidationResult(
                rule_name=f"range({column})", passed=passed, severity=severity,
                message=f"{violations} values out of range" if not passed else "OK",
            )
        elif rule_type == "allowed_values":
            if column not in df.columns:
                return ValidationResult(
                    rule_name=f"enum({column})", passed=False, severity=severity,
                    message=f"Column '{column}' not found",
                )
            invalid = ~df[column].isin(rule["values"])
            count = invalid.sum()
            passed = count == 0
            return ValidationResult(
                rule_name=f"enum({column})", passed=passed, severity=severity,
                message=f"{count} invalid values" if not passed else "OK",
            )
        elif rule_type == "uniqueness":
            cols = rule["columns"]
            dupes = df.duplicated(subset=cols, keep="first").sum()
            return ValidationResult(
                rule_name=f"unique({','.join(cols)})", passed=dupes == 0,
                severity=severity,
                message=f"{dupes} duplicate rows" if dupes else "OK",
            )
        return ValidationResult(rule_name="unknown", passed=True, severity=severity, message="Unknown rule")
