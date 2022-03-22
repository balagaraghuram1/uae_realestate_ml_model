"""Unit tests for feature engineering pipeline."""
import pytest
import pandas as pd
import numpy as np
from src.data.processors.feature_engineering import FeatureEngineer

@pytest.fixture
def property_data():
    return pd.DataFrame({
        "price_aed": [1500000, 2000000, 800000, 3500000, 1200000],
        "size_sqft": [1450, 2000, 800, 3500, 1200],
        "bedrooms": [2, 3, 1, 4, 2],
        "bathrooms": [2, 3, 1, 4, 2],
        "area": ["Dubai Marina", "Palm Jumeirah", "JVC", "Downtown Dubai", "Business Bay"],
        "emirate": ["dubai", "dubai", "dubai", "dubai", "dubai"],
        "property_type": ["apartment", "villa", "apartment", "penthouse", "apartment"],
        "latitude": [25.08, 25.11, 25.06, 25.19, 25.18],
        "longitude": [55.14, 55.12, 55.28, 55.27, 55.26],
        "created_at": pd.to_datetime(["2022-01-15", "2022-02-20", "2022-03-10", "2022-01-05", "2022-04-01"]),
    })

class TestFeatureEngineer:
    def test_fit_transform_creates_features(self, property_data):
        fe = FeatureEngineer()
        result = fe.fit_transform(property_data)
        assert len(result.columns) > len(property_data.columns)

    def test_price_features_created(self, property_data):
        fe = FeatureEngineer()
        result = fe.fit_transform(property_data)
        assert "price_log" in result.columns
        assert "price_per_sqft" in result.columns
        assert "price_per_bedroom" in result.columns

    def test_location_features_created(self, property_data):
        fe = FeatureEngineer()
        result = fe.fit_transform(property_data)
        assert "is_prime_area" in result.columns
        assert "is_dubai" in result.columns
        assert "emirate_rank" in result.columns

    def test_cluster_features_created(self, property_data):
        fe = FeatureEngineer()
        result = fe.fit_transform(property_data)
        assert "cluster" in result.columns

    def test_transform_uses_fitted_encoders(self, property_data):
        fe = FeatureEngineer()
        fe.fit_transform(property_data)
        new_data = property_data.head(2).copy()
        new_data["emirate"] = ["sharjah", "dubai"]
        result = fe.transform(new_data)
        assert "emirate_encoded" in result.columns

    def test_transform_fails_before_fit(self, property_data):
        fe = FeatureEngineer()
        with pytest.raises(RuntimeError):
            fe.transform(property_data)

    def test_all_numeric_features_finite(self, property_data):
        fe = FeatureEngineer()
        result = fe.fit_transform(property_data)
        numeric_cols = result.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            assert result[col].replace([np.inf, -np.inf], np.nan).isna().sum() == 0
