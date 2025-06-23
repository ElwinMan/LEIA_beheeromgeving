from pydantic import BaseModel
from typing import Optional, Dict, Any


class LayerBase(BaseModel):
    type: str
    title: str
    url: str
    featureName: Optional[str]
    isBackground: bool
    defaultOn: bool
    content: Optional[Dict[str, Any]] = None

class LayerCreate(LayerBase):
    pass

class LayerUpdate(BaseModel):
    type: Optional[str]
    title: Optional[str]
    url: Optional[str]
    featureName: Optional[str]
    isBackground: Optional[bool]
    defaultOn: Optional[bool]
    content: Optional[Dict[str, Any]]

class LayerResponse(LayerBase):
    id: int

    class Config:
        orm_mode = True