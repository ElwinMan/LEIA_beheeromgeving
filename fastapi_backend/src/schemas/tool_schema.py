from pydantic import BaseModel, field_serializer
from typing import Optional, Dict, Any, List
from datetime import datetime

class ToolBase(BaseModel):
    name: str
    description: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    last_updated: datetime

    @field_serializer("last_updated")
    def format_last_updated(self, value: datetime) -> str:
        return value.isoformat()


class ToolCreate(ToolBase):
    pass

class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[Dict[str, Any]] = None

class ToolResponse(ToolBase):
    id: int

    model_config = {
        "from_attributes": True
    }

class PaginatedToolsResponse(BaseModel):
    results: List[ToolResponse]
    total: int
    page: int
    page_size: int