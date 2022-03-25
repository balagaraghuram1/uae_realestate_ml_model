"""Unit tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

class TestHealthEndpoint:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_has_version(self):
        response = client.get("/health")
        assert "version" in response.json()

class TestRootEndpoint:
    def test_root_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200

class TestPropertiesEndpoint:
    def test_list_properties_returns_200(self):
        response = client.get("/api/v1/properties/")
        assert response.status_code == 200

    def test_invalid_emirate_returns_400(self):
        response = client.get("/api/v1/properties/?emirate=india")
        assert response.status_code == 400

    def test_valid_emirate_filter(self):
        response = client.get("/api/v1/properties/?emirate=dubai")
        assert response.status_code == 200

class TestPredictionsEndpoint:
    def test_price_prediction(self):
        response = client.post("/api/v1/predictions/price", json={
            "emirate": "dubai", "area": "Dubai Marina",
            "bedrooms": 2, "bathrooms": 2, "size_sqft": 1450,
        })
        assert response.status_code == 200
        assert "predicted_price" in response.json()

    def test_invalid_emirate_prediction(self):
        response = client.post("/api/v1/predictions/price", json={
            "emirate": "usa", "area": "New York",
            "bedrooms": 2, "bathrooms": 2, "size_sqft": 1450,
        })
        assert response.status_code == 400

class TestAnalyticsEndpoint:
    def test_market_overview(self):
        response = client.get("/api/v1/analytics/market")
        assert response.status_code == 200
        assert "summary" in response.json()

    def test_hotspots(self):
        response = client.get("/api/v1/analytics/hotspots")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
