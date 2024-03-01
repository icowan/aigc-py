import json
import typing

from pydantic import BaseModel
from starlette.responses import Response


class ErrorException(Exception):
    def __init__(self, message: str = '', code: int = 500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ErrorResponse(Response):
    def __init__(self, message: str = '', code: int = 500):
        self.message = message
        self.code = code
        super().__init__(status_code=code, content=message)

    """Error response model"""
    code: int = 500
    """Error code"""
    message: str = ''
    """Error message"""
    traceId: str = ''
    """Trace ID"""
    success: bool = False
    """Success flag"""

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            {
                "code": self.code,
                "message": self.message,
                "traceId": self.traceId,
                "success": self.success,
            },
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


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
