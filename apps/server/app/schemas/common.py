from pydantic import BaseModel
from typing import Any, Optional, Generic, TypeVar, List

T = TypeVar("T")

class ResponseModel(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[dict] = None

class PaginatedData(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
