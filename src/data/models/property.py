"""Property data models with strict validation."""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, validator

class Emirate(str, Enum):
    ABU_DHABI = "abu_dhabi"
    DUBAI = "dubai"
    SHARJAH = "sharjah"
    AJMAN = "ajman"
    UMM_AL_QUWAIN = "umm_al_quwain"
    RAS_AL_KHAIMAH = "ras_al_khaimah"
    FUJAIRAH = "fujairah"

class PropertyType(str, Enum):
    APARTMENT = "apartment"
    VILLA = "villa"
    TOWNHOUSE = "townhouse"
    PENTHOUSE = "penthouse"
    COMMERCIAL = "commercial"
    LAND = "land"
    INDUSTRIAL = "industrial"
    MIXED_USE = "mixed_use"

class PropertyStatus(str, Enum):
    AVAILABLE = "available"
    SOLD = "sold"
    RENTED = "rented"
    UNDER_CONSTRUCTION = "under_construction"
    OFF_PLAN = "off_plan"

class PropertyListing(BaseModel):
    """Core property listing model with comprehensive validation."""
    id: Optional[int] = None
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = None
    property_type: PropertyType
    status: PropertyStatus = PropertyStatus.AVAILABLE
    emirate: Emirate
    area: str = Field(..., min_length=2, max_length=100)
    sub_area: Optional[str] = None
    building_name: Optional[str] = None
    floor_number: Optional[int] = None
    unit_number: Optional[str] = None
    bedrooms: int = Field(..., ge=0, le=20)
    bathrooms: int = Field(..., ge=0, le=20)
    size_sqft: float = Field(..., gt=0, le=100000)
    plot_size_sqft: Optional[float] = None
    price_aed: float = Field(..., gt=0)
    price_per_sqft: Optional[float] = None
    service_charge_aed: Optional[float] = None
    furnished: bool = False
    parking_spaces: int = Field(0, ge=0)
    amenities: List[str] = []
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    developer: Optional[str] = None
    completion_year: Optional[int] = Field(None, ge=2000, le=2030)
    agent_name: Optional[str] = None
    agent_contact: Optional[str] = None
    reference_number: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source: str = "manual"

    @validator("price_per_sqft", always=True)
    def compute_price_per_sqft(cls, v, values):
        if v is not None:
            return v
        if "price_aed" in values and "size_sqft" in values and values["size_sqft"] > 0:
            return round(values["price_aed"] / values["size_sqft"], 2)
        return None

    @validator("title")
    def title_not_placeholder(cls, v):
        placeholders = ["test", "untitled", "sample", "new listing"]
        if v.lower().strip() in placeholders:
            raise ValueError("Title must be descriptive, not a placeholder")
        return v.strip()

    class Config:
        use_enum_values = True
        validate_assignment = True

class PropertyTransaction(BaseModel):
    """Historical transaction record."""
    id: Optional[int] = None
    property_id: Optional[int] = None
    transaction_type: str  # "sale", "rent", "mortgage"
    price_aed: float = Field(..., gt=0)
    transaction_date: datetime
    buyer_type: Optional[str] = None  # "individual", "company", "investor"
    mortgage_amount: Optional[float] = None
    registration_fee: Optional[float] = None
    source: str = "dld"

    class Config:
        use_enum_values = True

class AreaStatistics(BaseModel):
    """Aggregated statistics for a geographic area."""
    area: str
    emirate: Emirate
    avg_price: float
    median_price: float
    price_std: float
    avg_size_sqft: float
    total_listings: int
    avg_price_per_sqft: float
    popular_property_types: List[str]
    price_trend_6m: Optional[float] = None
    price_trend_12m: Optional[float] = None
    computed_at: datetime = Field(default_factory=datetime.utcnow)
