from pydantic import BaseModel
from typing import Dict, Any

class ViewerBase(BaseModel):
    content: Dict[str, Any]

class ViewerCreate(ViewerBase):
    digital_twin_id: int

class ViewerUpdate(BaseModel):
    content: Dict[str, Any]

class ViewerResponse(ViewerBase):
    id: int

    class Config:
        orm_mode = True