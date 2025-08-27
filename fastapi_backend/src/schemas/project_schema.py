from pydantic import BaseModel, field_serializer
from typing import Optional, Any, List
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    content: Optional[Any] = None
    last_updated: datetime

    @field_serializer("last_updated")
    def format_last_updated(self, value: datetime) -> str:
        return value.isoformat()

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[Any] = None

class ProjectResponse(ProjectBase):
    id: int

    class Config:
        orm_mode = True

class PaginatedProjectsResponse(BaseModel):
    results: List[ProjectResponse]
    total: int
    page: int
    page_size: int