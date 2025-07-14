from pydantic import BaseModel, ConfigDict
from typing import Dict, Any

class ViewerBase(BaseModel):
    content: Dict[str, Any]

class ViewerCreate(ViewerBase):
    digital_twin_id: int

class ViewerUpdate(BaseModel):
    content: Dict[str, Any]

class ViewerResponse(BaseModel):
    id: int
    content: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)