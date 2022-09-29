 """Standardized API error codes and responses."""
from fastapi import HTTPException
from typing import Optional

class ErrorCode:
    INVALID_EMIRATE = "E1001"
    INVALID_PROPERTY_TYPE = "E1002"
    PRICE_OUT_OF_RANGE = "E1003"
    SIZE_OUT_OF_RANGE = "E1004"
    DATA_NOT_FOUND = "E2001"
    MODEL_NOT_LOADED = "E3001"
    PREDICTION_FAILED = "E3002"
    RATE_LIMIT_EXCEEDED = "E4001"
    INTERNAL_ERROR = "E5001"

class APIError(HTTPException):
    """Custom API error with error code."""
    def __init__(self, status_code: int, code: str, message: str,
                 details: Optional[dict] = None):
        super().__init__(status_code=status_code, detail={
            "error_code": code, "message": message, "details": details or {},
        })

def invalid_emirate(emirate: str):
    raise APIError(400, ErrorCode.INVALID_EMIRATE,
                   f"Invalid emirate '{emirate}'. Must be one of the seven UAE emirates.")

def data_not_found(resource: str, identifier: str):
    raise APIError(404, ErrorCode.DATA_NOT_FOUND,
                   f"{resource} with identifier '{identifier}' not found.")

def model_not_loaded(model_name: str):
    raise APIError(503, ErrorCode.MODEL_NOT_LOADED,
                   f"Model '{model_name}' is not currently loaded.")
