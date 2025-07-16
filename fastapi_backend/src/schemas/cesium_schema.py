from pydantic import BaseModel
from typing import Optional, Any

class CesiumBase(BaseModel):
    url: str
    vertexNormals: Optional[str] = None
    content: Optional[Any] = None

class CesiumCreate(CesiumBase):
    pass

class CesiumUpdate(BaseModel):
    url: Optional[str] = None
    vertexNormals: Optional[str] = None
    content: Optional[Any] = None

class CesiumResponse(CesiumBase):
    id: int

    class Config:
        orm_mode = True