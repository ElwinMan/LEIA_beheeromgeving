from pydantic import BaseModel, field_serializer
from typing import Optional, Dict, Any, List
from datetime import datetime

class LayerBase(BaseModel):
    type: str
    title: str
    url: str
    featureName: Optional[str]
    isBackground: bool
    content: Optional[Dict[str, Any]] = None
    last_updated: datetime

    @field_serializer("last_updated")
    def format_last_updated(self, value: datetime) -> str:
        return value.isoformat()

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

    model_config = {
        "from_attributes": True
    }

class PaginatedLayersResponse(BaseModel):
    results: List[LayerResponse]
    total: int
    page: int
    page_size: int