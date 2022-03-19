"""Unit tests for the data cleaning pipeline."""
import pytest
import pandas as pd
import numpy as np
from src.data.processors.cleaning_pipeline import CleaningPipeline

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "title": ["Luxury Apartment" * 5, "Test"],
        "price_aed": [1500000, 2000000, 50000, 3000000, 1800000, -100],
        "size_sqft": [1450, 2000, 800, 3500, 1600, 1200],
        "bedrooms": [2, 3, 1, 4, 2, 2],
        "bathrooms": [2, 3, 1, 4, 2, 2],
        "area": ["Dubai Marina", "Palm Jumeirah", "JVC", "Downtown", "Business Bay", ""],
        "emirate": ["dubai", "dubai", "dubai", "dubai", "dubai", "dubai"],
        "property_type": ["apartment", "villa", "apartment", "penthouse", "apartment", "apartment"],
    })

class TestCleaningPipeline:
    def test_removes_duplicates(self, sample_data):
        duped = pd.concat([sample_data, sample_data.head(2)])
        pipeline = CleaningPipeline()
        result, report = pipeline.run(duped)
        assert report.removed_duplicates >= 2

    def test_removes_null_prices(self, sample_data):
        df = sample_data.copy()
        df.loc[0, "price_aed"] = np.nan
        pipeline = CleaningPipeline()
        result, _ = pipeline.run(df)
        assert result["price_aed"].isna().sum() == 0

    def test_enforces_price_bounds(self, sample_data):
        pipeline = CleaningPipeline()
        result, report = pipeline.run(sample_data)
        assert (result["price_aed"] >= 10000).all()
        assert (result["price_aed"] <= 500000000).all()

    def test_standardizes_area_names(self, sample_data):
        pipeline = CleaningPipeline()
        result, _ = pipeline.run(sample_data)
        for area in result["area"]:
            assert area == area.strip().title()

    def test_computes_price_per_sqft(self, sample_data):
        pipeline = CleaningPipeline()
        result, _ = pipeline.run(sample_data)
        if "price_per_sqft" in result.columns:
            expected = result["price_aed"] / result["size_sqft"]
            pd.testing.assert_series_equal(
                result["price_per_sqft"], expected.round(2), check_names=False
            )

    def test_handles_empty_dataframe(self):
        pipeline = CleaningPipeline()
        df = pd.DataFrame()
        result, report = pipeline.run(df)
        assert report.total_rows == 0
        assert len(result) == 0

    def test_report_generation(self, sample_data):
        pipeline = CleaningPipeline()
        _, report = pipeline.run(sample_data)
        assert report.total_rows == len(sample_data)
        assert isinstance(report.warnings, list)
