import re
from typing import Optional, Dict, Any, List
from datetime import date


class PropertyValidator:
    EMIRATES = ["abu_dhabi", "dubai", "sharjah", "ajman", "umm_al_quwain", "ras_al_khaimah", "fujairah"]
    PROPERTY_TYPES = ["apartment", "villa", "townhouse", "penthouse", "commercial", "land"]

    @staticmethod
    def validate_emirate(value: str) -> bool:
        return value.lower() in PropertyValidator.EMIRATES

    @staticmethod
    def validate_property_type(value: str) -> bool:
        return value.lower() in PropertyValidator.PROPERTY_TYPES

    @staticmethod
    def validate_price(value: float) -> bool:
        return value > 0 and value < 1_000_000_000

    @staticmethod
    def validate_size(value: float) -> bool:
        return value > 0 and value < 1_000_000

    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        return 24.0 <= lat <= 26.5 and 51.5 <= lon <= 56.5

    @staticmethod
    def validate_uae_phone(value: str) -> bool:
        return bool(re.match(r"^(?:\+971|00971|0)?[0-9]{9,10}$", value))

    @staticmethod
    def validate_email(value: str) -> bool:
        return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value))

    @staticmethod
    def validate_emei_number(value: str) -> bool:
        return bool(re.match(r"^\d{10,15}$", value))

    @staticmethod
    def sanitize_string(value: str) -> str:
        return " ".join(value.strip().split())


class DataQualityReport:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats: Dict[str, Any] = {}

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def record_stat(self, key: str, value: Any) -> None:
        self.stats[key] = value

    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.is_valid(),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "stats": self.stats,
        }
