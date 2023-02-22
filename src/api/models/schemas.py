from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime


class PropertyBase(BaseModel):
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    property_type: str = Field(..., pattern="^(apartment|villa|townhouse|penthouse|commercial|land)$")
    emirate: str = Field(..., pattern="^(abu_dhabi|dubai|sharjah|ajman|umm_al_quwain|ras_al_khaimah|fujairah)$")
    area: str = Field(..., max_length=200)
    bedrooms: int = Field(..., ge=0, le=50)
    bathrooms: int = Field(..., ge=0, le=50)
    size_sqft: float = Field(..., gt=0)
    price_aed: float = Field(..., gt=0)
    latitude: Optional[float] = Field(None, ge=24.0, le=26.5)
    longitude: Optional[float] = Field(None, ge=51.5, le=56.5)
    listing_date: Optional[date] = None
    furnished: Optional[bool] = None
    amenities: Optional[List[str]] = None


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price_aed: Optional[float] = None
    furnished: Optional[bool] = None
    amenities: Optional[List[str]] = None


class PropertyResponse(PropertyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    price_per_sqft: Optional[float] = None
    days_on_market: Optional[int] = None
    predicted_value: Optional[float] = None
    confidence_score: Optional[float] = None

    class Config:
        from_attributes = True


class PropertySearchParams(BaseModel):
    emirate: Optional[str] = None
    property_type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_size: Optional[float] = None
    max_size: Optional[float] = None
    area: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$")


class PaginatedResponse(BaseModel):
    items: List[PropertyResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PricePredictionRequest(BaseModel):
    property_type: str
    emirate: str
    area: str
    bedrooms: int
    bathrooms: int
    size_sqft: float
    furnished: Optional[bool] = None
    amenities: Optional[List[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PricePredictionResponse(BaseModel):
    predicted_price: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    prediction_model: str
    feature_importance: Optional[Dict[str, float]] = None
    comparable_properties: Optional[List[Dict[str, Any]]] = None


class DemandForecastRequest(BaseModel):
    emirate: str
    property_type: Optional[str] = None
    area: Optional[str] = None
    forecast_months: int = Field(default=12, ge=1, le=60)


class DemandForecastResponse(BaseModel):
    emirate: str
    property_type: Optional[str] = None
    forecasts: List[Dict[str, Any]]
    seasonality: Optional[Dict[str, float]] = None
    trend_direction: str
    confidence_level: float


class RiskAssessmentRequest(BaseModel):
    property_id: Optional[int] = None
    emirate: str
    area: str
    property_type: str
    price_aed: float
    investment_horizon_years: int = Field(default=5, ge=1, le=30)


class RiskAssessmentResponse(BaseModel):
    overall_risk_score: float
    risk_factors: Dict[str, float]
    market_risk: float
    liquidity_risk: float
    regulatory_risk: float
    recommendation: str
    suggested_actions: List[str]


class MarketAnalyticsRequest(BaseModel):
    emirate: Optional[str] = None
    property_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    granularity: str = Field(default="monthly", pattern="^(daily|weekly|monthly|quarterly|yearly)$")


class MarketAnalyticsResponse(BaseModel):
    summary: Dict[str, Any]
    price_trends: List[Dict[str, Any]]
    volume_trends: List[Dict[str, Any]]
    top_areas: List[Dict[str, Any]]
    distribution: Dict[str, Any]
