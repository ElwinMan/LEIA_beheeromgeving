from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class ToolBase(BaseModel):
    name: str
    content: Optional[Dict[str, Any]] = None

class ToolCreate(ToolBase):
    pass

class ToolUpdate(BaseModel):
    name: Optional[str] = None
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