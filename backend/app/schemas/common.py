from typing import Generic, TypeVar, Sequence
from pydantic import BaseModel
import math

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    limit: int
    pages: int

    @classmethod
    def create(cls, items: Sequence[T], total: int, page: int, limit: int):
        pages = math.ceil(total / limit) if limit > 0 else 1
        return cls(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )
