import typing

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Error response model"""
    code: int = 500
    """Error code"""
    message: str = ''
    """Error message"""
    traceId: str = ''
    """Trace ID"""
    success: bool = False
    """Success flag"""


class SuccessResponse(BaseModel):
    """Success response model"""
    code: int = 200
    """Success code"""
    message: str = ''
    """Success message"""
    data: typing.Any = None
    """Success data"""
    traceId: str = ''
    """Trace ID"""
    success: bool = True
    """Success flag"""
