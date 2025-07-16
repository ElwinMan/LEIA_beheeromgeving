from pydantic import BaseModel
from typing import Optional, Any

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    content: Optional[Any] = None

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