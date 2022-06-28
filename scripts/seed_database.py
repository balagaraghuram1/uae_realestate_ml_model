"""Seed database with sample data for development."""
import random, logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

AREAS = {
    "dubai": ["Dubai Marina", "Palm Jumeirah", "Downtown Dubai", "JBR", "Business Bay",
              "JVC", "Dubai Hills Estate", "Arabian Ranches", "Motor City"],
    "abu_dhabi": ["Al Reem Island", "Saadiyat Island", "Yas Island", "Corniche", "Khalifa City"],
    "sharjah": ["Al Nahda", "Al Majaz", "Al Khan", "University City"],
}

PRICE_RANGES = {
    "apartment": (400000, 5000000),
    "villa": (1500000, 20000000),
    "townhouse": (800000, 8000000),
    "penthouse": (3000000, 30000000),
    "commercial": (500000, 10000000),
}

def generate_listing(emirate: str = "dubai") -> dict:
    """Generate a realistic property listing."""
    property_type = random.choice(["apartment", "villa", "townhouse", "penthouse", "commercial"])
    area = random.choice(AREAS.get(emirate, ["Unknown Area"]))
    bedrooms = random.randint(0, 5) if property_type != "commercial" else 0
    bathrooms = max(1, bedrooms - random.randint(0, 1)) if bedrooms > 0 else 1
    size = random.randint(400, 8000)
    price_min, price_max = PRICE_RANGES.get(property_type, (500000, 5000000))
    price = random.randint(price_min, price_max)
    return {
        "title": f"{property_type.title()} in {area}",
        "property_type": property_type, "emirate": emirate, "area": area,
        "bedrooms": bedrooms, "bathrooms": bathrooms,
        "size_sqft": size, "price_aed": price,
        "furnished": random.choice([True, False]),
        "created_at": datetime.utcnow() - timedelta(days=random.randint(0, 365)),
    }

def seed_data(db_manager, n: int = 500):
    """Seed database with n sample listings."""
    for _ in range(n):
        emirate = random.choice(list(AREAS.keys()))
        listing = generate_listing(emirate)
        db_manager.save_property(listing)
    logger.info("Seeded %d listings", n)
