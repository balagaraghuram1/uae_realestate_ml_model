 """End-to-end tests for the complete ML pipeline."""
import pytest, tempfile, os
import pandas as pd
import numpy as np
from src.data.processors.cleaning_pipeline import CleaningPipeline
from src.data.processors.feature_engineering import FeatureEngineer

@pytest.fixture
def full_dataset():
    np.random.seed(42)
    n = 500
    return pd.DataFrame({
        "title": [f"Property {i}" for i in range(n)],
        "price_aed": np.random.lognormal(14, 0.8, n),
        "size_sqft": np.random.lognormal(7, 0.5, n),
        "bedrooms": np.random.randint(0, 6, n),
        "bathrooms": np.random.randint(1, 5, n),
        "area": np.random.choice(["Dubai Marina", "Palm Jumeirah", "JVC"], n),
        "emirate": np.random.choice(["dubai", "abu_dhabi"], n),
        "property_type": np.random.choice(["apartment", "villa"], n),
    })

class TestEndToEnd:
    def test_full_pipeline(self, full_dataset):
        cleaner = CleaningPipeline()
        cleaned, report = cleaner.run(full_dataset)
        assert len(cleaned) > 0
        engineer = FeatureEngineer()
        features = engineer.fit_transform(cleaned)
        assert len(features.columns) > len(cleaned.columns) + 5
        assert not features.empty

    def test_pipeline_preserves_data_integrity(self, full_dataset):
        cleaner = CleaningPipeline()
        cleaned, _ = cleaner.run(full_dataset)
        assert "price_aed" in cleaned.columns
        assert "size_sqft" in cleaned.columns
        assert cleaned["price_aed"].min() > 0
        assert cleaned["size_sqft"].min() > 0
