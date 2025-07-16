from pydantic import BaseModel
from typing import Optional, Any

class StorySnippetBase(BaseModel):
    name: str
    description: Optional[str] = None
    content: Optional[Any] = None

class StorySnippetCreate(StorySnippetBase):
    pass

class StorySnippetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[Any] = None

class StorySnippetResponse(StorySnippetBase):
    id: int

    class Config:
        orm_mode = True