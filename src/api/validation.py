"""Advanced request validation using Pydantic."""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class PropertyFilter(BaseModel):
    """Validated property search filters."""
    emirate: Optional[str] = None
    property_type: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    min_bedrooms: Optional[int] = Field(None, ge=0, le=20)
    max_bedrooms: Optional[int] = Field(None, ge=0, le=20)
    min_size: Optional[float] = Field(None, ge=0)
    max_size: Optional[float] = Field(None, ge=0)
    sort_by: str = "price_aed"
    sort_order: SortOrder = SortOrder.ASC
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

    @validator("emirate")
    def validate_emirate(cls, v):
        if v and v.lower() not in ["abu_dhabi","dubai","sharjah","ajman","umm_al_quwain","ras_al_khaimah","fujairah"]:
            raise ValueError("Invalid UAE emirate")
        return v.lower() if v else v

class PredictionInput(BaseModel):
    """Validated prediction request."""
    emirate: str
    area: str
    property_type: str = "apartment"
    bedrooms: int = Field(2, ge=0, le=20)
    bathrooms: int = Field(2, ge=0, le=15)
    size_sqft: float = Field(..., gt=0, le=100000)
