from pydantic import BaseModel, field_serializer
from typing import Optional, List
from datetime import datetime

class BookmarkBase(BaseModel):
    title: str
    description: Optional[str] = None
    x: float
    y: float
    z: float
    heading: float
    pitch: float
    duration: float
    last_updated: datetime

    @field_serializer("last_updated")
    def format_last_updated(self, value: datetime) -> str:
        return value.isoformat()

class BookmarkCreate(BookmarkBase):
    pass

class BookmarkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    heading: Optional[float] = None
    pitch: Optional[float] = None
    duration: Optional[float] = None

class BookmarkResponse(BookmarkBase):
    id: int

    class Config:
        orm_mode = True

# New schema for bookmark tool associations (with reference to actual bookmark)
class BookmarkToolAssociationCreate(BaseModel):
    bookmark_id: int
    sort_order: Optional[int] = 0

class BookmarkToolAssociationResponse(BaseModel):
    id: int
    tool_id: int
    content_type_id: Optional[int] = None
    content_id: int  # This will be the bookmark_id
    sort_order: int
    # Include the actual bookmark data
    bookmark: Optional[BookmarkResponse] = None

    class Config:
        orm_mode = True

class PaginatedBookmarksResponse(BaseModel):
    results: List[BookmarkResponse]
    total: int
    page: int
    page_size: int