"""Integration tests for the data processing pipeline."""
import pytest
import pandas as pd
import numpy as np
from src.data.processors.cleaning_pipeline import CleaningPipeline
from src.data.processors.feature_engineering import FeatureEngineer
from src.data.validators.schema_validator import SchemaValidator

@pytest.fixture
def raw_property_data():
    np.random.seed(42)
    n = 200
    return pd.DataFrame({
        "title": [f"Property {i}" for i in range(n)],
        "price_aed": np.random.lognormal(14, 0.8, n),
        "size_sqft": np.random.lognormal(7, 0.5, n),
        "bedrooms": np.random.randint(0, 6, n),
        "bathrooms": np.random.randint(1, 5, n),
        "area": np.random.choice(["Dubai Marina", "Palm Jumeirah", "JVC", "Downtown"], n),
        "emirate": np.random.choice(["dubai", "abu_dhabi", "sharjah"], n),
        "property_type": np.random.choice(["apartment", "villa", "townhouse"], n),
        "latitude": np.random.uniform(24.5, 25.5, n),
        "longitude": np.random.uniform(55, 56, n),
    })

class TestDataPipeline:
    def test_clean_then_engineer(self, raw_property_data):
        cleaner = CleaningPipeline()
        cleaned, report = cleaner.run(raw_property_data)
        assert len(cleaned) > 0
        assert report.total_rows == len(raw_property_data)
        engineer = FeatureEngineer()
        features = engineer.fit_transform(cleaned)
        assert len(features.columns) > len(cleaned.columns)

    def test_validation_passes_after_cleaning(self, raw_property_data):
        cleaner = CleaningPipeline()
        cleaned, _ = cleaner.run(raw_property_data)
        validator = SchemaValidator()
        validator.add_not_null(["price_aed", "size_sqft", "area"])
        validator.add_range("price_aed", min_val=10000, max_val=500000000)
        validator.add_range("bedrooms", min_val=0, max_val=20)
        report = validator.validate(cleaned)
        assert report.passed >= report.total_checks * 0.8

    def test_full_pipeline(self, raw_property_data):
        cleaner = CleaningPipeline()
        cleaned, _ = cleaner.run(raw_property_data)
        engineer = FeatureEngineer()
        features = engineer.fit_transform(cleaned)
        validator = SchemaValidator()
        validator.add_not_null(["price_aed", "size_sqft"])
        report = validator.validate(features)
        assert report.total_checks > 0
