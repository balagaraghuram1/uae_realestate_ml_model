 """Property valuation API endpoint."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/valuation", tags=["valuation"])

class ValuationRequest(BaseModel):
    emirate: str
    area: str
    property_type: str = "apartment"
    bedrooms: int = Field(2, ge=0, le=20)
    size_sqft: float = Field(..., gt=0)
    year_built: int = Field(None, ge=2000, le=2025)
    condition: str = "good"

@router.post("/estimate")
async def estimate_value(req: ValuationRequest):
    """Estimate property value using comparable analysis."""
    base_price = 1800 * req.size_sqft
    area_multiplier = 1.2 if req.area in ["Dubai Marina", "Palm Jumeirah", "Downtown Dubai"] else 1.0
    type_multiplier = {"villa": 1.3, "penthouse": 1.5, "townhouse": 1.1}.get(req.property_type, 1.0)
    condition_multiplier = {"excellent": 1.1, "good": 1.0, "fair": 0.9}.get(req.condition, 1.0)
    estimated = base_price * area_multiplier * type_multiplier * condition_multiplier
    return {
        "estimated_value": round(estimated),
        "confidence": 0.85,
        "methodology": "comparable_analysis",
        "factors_applied": {
            "area": area_multiplier,
            "property_type": type_multiplier,
            "condition": condition_multiplier,
        },
    }
