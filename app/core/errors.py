"""Application specific errors and exceptions."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel

__all__ = ["ErrorCode", "AppError", "ErrorResponse", "to_response"]

class ErrorCode(str, Enum):
    """Standard error codes."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    PIPELINE_ERROR = "PIPELINE_ERROR"
    EXTRACTION_ERROR = "EXTRACTION_ERROR"
    GROUNDING_ERROR = "GROUNDING_ERROR"
    TIER_ERROR = "TIER_ERROR"
    SCORING_ERROR = "SCORING_ERROR"
    GENERATION_ERROR = "GENERATION_ERROR"
    VALIDATION_BLOCKED = "VALIDATION_BLOCKED"
    INTERNAL_ERROR = "INTERNAL_ERROR"

class AppError(Exception):
    """Base exception for application errors."""
    def __init__(self, code: ErrorCode, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details

class ErrorResponse(BaseModel):
    """Error response model."""
    code: str
    message: str
    details: dict[str, Any] | None = None
    timestamp: datetime

def to_response(error: AppError) -> ErrorResponse:
    """Convert an AppError to an ErrorResponse."""
    return ErrorResponse(
        code=error.code.value,
        message=error.message,
        details=error.details,
        timestamp=datetime.now(timezone.utc)
    )