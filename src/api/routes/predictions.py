from fastapi import APIRouter, HTTPException

from src.api.models.schemas import (
    PricePredictionRequest, PricePredictionResponse,
    DemandForecastRequest, DemandForecastResponse,
    RiskAssessmentRequest, RiskAssessmentResponse,
)

router = APIRouter()


@router.post("/price", response_model=PricePredictionResponse)
async def predict_price(request: PricePredictionRequest):
    raise HTTPException(status_code=501, detail="Model not deployed")


@router.post("/demand", response_model=DemandForecastResponse)
async def forecast_demand(request: DemandForecastRequest):
    raise HTTPException(status_code=501, detail="Model not deployed")


@router.post("/yield", response_model=dict)
async def predict_rental_yield(
    property_type: str,
    emirate: str,
    area: str,
    purchase_price: float,
    bedrooms: int = 1,
    annual_maintenance: float = 0,
):
    return {
        "predicted_monthly_rent": 0,
        "gross_yield_pct": 0,
        "net_yield_pct": 0,
        "payback_years": 0,
        "cash_flow_positive": False,
        "confidence": 0,
    }


@router.post("/risk", response_model=RiskAssessmentResponse)
async def assess_risk(request: RiskAssessmentRequest):
    raise HTTPException(status_code=501, detail="Model not deployed")


@router.get("/models", response_model=list)
async def list_available_models():
    return [
        {
            "id": "price_prediction_v1",
            "name": "Price Prediction",
            "type": "regression",
            "status": "development",
            "metrics": {},
            "last_trained": None,
        },
        {
            "id": "demand_forecast_v1",
            "name": "Demand Forecast",
            "type": "time_series",
            "status": "development",
            "metrics": {},
            "last_trained": None,
        },
        {
            "id": "rental_yield_v1",
            "name": "Rental Yield Prediction",
            "type": "regression",
            "status": "development",
            "metrics": {},
            "last_trained": None,
        },
        {
            "id": "risk_assessment_v1",
            "name": "Risk Assessment",
            "type": "ensemble",
            "status": "development",
            "metrics": {},
            "last_trained": None,
        },
    ]
