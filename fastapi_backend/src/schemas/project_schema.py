from pydantic import BaseModel
from typing import Optional, Any

class ProjectSnippetBase(BaseModel):
    name: str
    description: Optional[str] = None
    content: Optional[Any] = None

class ProjectSnippetCreate(ProjectSnippetBase):
    pass

class ProjectSnippetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[Any] = None

class ProjectSnippetResponse(ProjectSnippetBase):
    id: int

    class Config:
        orm_mode = True