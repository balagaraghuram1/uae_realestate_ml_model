from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional

from api_models_schemas import (
    PropertySearchParams, PropertyResponse, PropertyCreate,
    PropertyUpdate, PaginatedResponse,
)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def search_properties(
    emirate: Optional[str] = Query(None),
    property_type: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    min_bedrooms: Optional[int] = Query(None),
    max_bedrooms: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    params = PropertySearchParams(
        emirate=emirate,
        property_type=property_type,
        min_price=min_price,
        max_price=max_price,
        min_bedrooms=min_bedrooms,
        max_bedrooms=max_bedrooms,
        page=page,
        page_size=page_size,
    )
    return {
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
        "total_pages": 0,
    }


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: int):
    raise HTTPException(status_code=404, detail="Property not found")


@router.post("/", response_model=PropertyResponse, status_code=201)
async def create_property(property_data: PropertyCreate):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(property_id: int, property_data: PropertyUpdate):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{property_id}", status_code=204)
async def delete_property(property_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{property_id}/comparables", response_model=list)
async def get_comparable_properties(
    property_id: int,
    limit: int = Query(10, ge=1, le=50),
):
    return []


@router.get("/{property_id}/price_history", response_model=list)
async def get_price_history(
    property_id: int,
    months: int = Query(12, ge=1, le=60),
):
    return []
