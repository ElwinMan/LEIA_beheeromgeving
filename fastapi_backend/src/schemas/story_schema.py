from pydantic import BaseModel, field_serializer
from typing import Optional, Any, List
from datetime import datetime

class StoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    content: Optional[Any] = None
    last_updated: datetime

    @field_serializer("last_updated")
    def format_last_updated(self, value: datetime) -> str:
        return value.isoformat()

class StoryCreate(StoryBase):
    pass

class StoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[Any] = None

class StoryResponse(StoryBase):
    id: int

    class Config:
        from_attributes = True

class PaginatedStoriesResponse(BaseModel):
    results: List[StoryResponse]
    total: int
    page: int
    page_size: int