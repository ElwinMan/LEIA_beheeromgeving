from pydantic import BaseModel
from typing import Optional, Any, List

class BookmarkBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[Any] = None

class BookmarkCreate(BookmarkBase):
    pass

class BookmarkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[Any] = None

class BookmarkResponse(BookmarkBase):
    id: int

    class Config:
        orm_mode = True

class PaginatedBookmarksResponse(BaseModel):
    results: List[BookmarkResponse]
    total: int
    page: int
    page_size: int