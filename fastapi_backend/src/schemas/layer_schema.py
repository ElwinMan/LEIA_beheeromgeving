from pydantic import BaseModel
from typing import Optional, Dict, Any

class LayerBase(BaseModel):
    type: str
    title: str
    url: str
    featureName: Optional[str]
    isBackground: bool
    content: Optional[Dict[str, Any]] = None

class LayerCreate(LayerBase):
    pass

class LayerUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    featureName: Optional[str] = None
    content: Optional[Dict[str, Any]] = None

class LayerResponse(LayerBase):
    id: int

    class Config:
        orm_mode = True