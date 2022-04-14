"""Data normalizer for standardizing property records across sources."""
import re, logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

AREA_ALIASES = {
    "dubai marina": "Dubai Marina",
    "marina": "Dubai Marina",
    "palm jumeirah": "Palm Jumeirah",
    "the palm": "Palm Jumeirah",
    "downtown": "Downtown Dubai",
    "downtown dubai": "Downtown Dubai",
    "jvc": "Jumeirah Village Circle",
    "jumeirah village circle": "Jumeirah Village Circle",
    "jbr": "Jumeirah Beach Residence",
    "jumeirah beach residence": "Jumeirah Beach Residence",
    "business bay": "Business Bay",
    "dubai hills": "Dubai Hills Estate",
    "dubai hills estate": "Dubai Hills Estate",
}

EMIRATE_ALIASES = {
    "dubai": "dubai",
    "abu dhabi": "abu_dhabi",
    "abudhabi": "abu_dhabi",
    "sharjah": "sharjah",
    "ajman": "ajman",
    "umm al quwain": "umm_al_quwain",
    "ras al khaimah": "ras_al_khaimah",
    "rak": "ras_al_khaimah",
    "fujairah": "fujairah",
}

class DataNormalizer:
    """Normalize and standardize property data from various sources."""

    def normalize_area(self, area: str) -> str:
        """Normalize area name."""
        clean = re.sub(r"\s+", " ", area.strip().lower())
        return AREA_ALIASES.get(clean, area.strip().title())

    def normalize_emirate(self, emirate: str) -> str:
        """Normalize emirate name."""
        clean = emirate.strip().lower()
        return EMIRATE_ALIASES.get(clean, clean)

    def normalize_price(self, price_text: str) -> float:
        """Parse various price formats to float AED."""
        if not price_text:
            return 0.0
        text = price_text.replace(",", "").replace("AED", "").replace("د.إ", "").strip()
        multiplier = 1.0
        if text.lower().endswith("k"):
            multiplier = 1000
            text = text[:-1]
        elif text.lower().endswith("m"):
            multiplier = 1000000
            text = text[:-1]
        elif "million" in text.lower():
            multiplier = 1000000
            text = re.sub(r"million", "", text, flags=re.IGNORECASE)
        try:
            return float(re.sub(r"[^\d.]", "", text)) * multiplier
        except ValueError:
            return 0.0

    def normalize_size(self, size_text: str) -> float:
        """Parse size text to square feet."""
        if not size_text:
            return 0.0
        text = size_text.lower().replace(",", "").strip()
        sqft_match = re.search(r"(\d+\.?\d*)\s*(sq\.?\s*ft|sqft|square\s*feet)", text)
        if sqft_match:
            return float(sqft_match.group(1))
        sqm_match = re.search(r"(\d+\.?\d*)\s*(sq\.?\s*m|sqm|square\s*meter)", text)
        if sqm_match:
            return float(sqm_match.group(1)) * 10.7639
        numbers = re.findall(r"\d+\.?\d*", text)
        return float(numbers[0]) if numbers else 0.0

    def normalize_property_type(self, ptype: str) -> str:
        """Normalize property type."""
        mapping = {
            "flat": "apartment", "apt": "apartment", "apartment": "apartment",
            "villa": "villa", "house": "villa",
            "townhouse": "townhouse", "town house": "townhouse",
            "penthouse": "penthouse", "ph": "penthouse",
            "office": "commercial", "shop": "commercial", "retail": "commercial",
            "land": "land", "plot": "land",
            "warehouse": "industrial", "factory": "industrial",
        }
        clean = ptype.strip().lower()
        return mapping.get(clean, clean)

    def normalize_record(self, record: Dict) -> Dict:
        """Normalize a complete property record."""
        return {
            **record,
            "area": self.normalize_area(record.get("area", "")),
            "emirate": self.normalize_emirate(record.get("emirate", "")),
            "price_aed": self.normalize_price(str(record.get("price_aed", ""))),
            "size_sqft": self.normalize_size(str(record.get("size_sqft", ""))),
            "property_type": self.normalize_property_type(record.get("property_type", "")),
        }
