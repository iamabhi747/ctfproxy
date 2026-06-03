from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

class ServerMethodRequest (BaseModel):
    plugin: str
    method: str
    args: list[Any]
    kwargs: dict[str, Any]

class DaemonMethodRequest (BaseModel):
    method: str
    args: list[Any]
    kwargs: dict[str, Any]


class ErrorType (Enum):
    VALIDATION = "ValidationError"
    INVALID_PLUGIN = "InvalidPlugin"
    INVALID_METHOD = "InvalidMethod"
    OPERATION = "OperationError"

class ErrorResponse (BaseModel):
    success: Literal[False]
    statuscode: int
    errtyepe: ErrorType
    errmessage: str
    detail: Any

class ResponseType (Enum):
    HEALTH = "Health"
    METHOD_OUTPUT = "MethodOutput"

class ResponseData (BaseModel):
    success: Literal[True]
    datatype: ResponseType
    data: Any


