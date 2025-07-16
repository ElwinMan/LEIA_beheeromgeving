from pydantic import BaseModel
from typing import Optional, Any

class BookmarkSnippetBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[Any] = None

class BookmarkSnippetCreate(BookmarkSnippetBase):
    pass

class BookmarkSnippetUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[Any] = None

class BookmarkSnippetResponse(BookmarkSnippetBase):
    id: int

    class Config:
        orm_mode = True