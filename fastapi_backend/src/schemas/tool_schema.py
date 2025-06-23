from pydantic import BaseModel
from typing import Optional, Dict, Any

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

    class Config:
        orm_mode = True