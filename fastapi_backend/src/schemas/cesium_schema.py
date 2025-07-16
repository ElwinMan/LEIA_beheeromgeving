from pydantic import BaseModel
from typing import Optional, Any

class CesiumSnippetBase(BaseModel):
    url: str
    vertexNormals: Optional[str] = None
    content: Optional[Any] = None

class CesiumSnippetCreate(CesiumSnippetBase):
    pass

class CesiumSnippetUpdate(BaseModel):
    url: Optional[str] = None
    vertexNormals: Optional[str] = None
    content: Optional[Any] = None

class CesiumSnippetResponse(CesiumSnippetBase):
    id: int

    class Config:
        orm_mode = True