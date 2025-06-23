from pydantic import BaseModel
from typing import Optional

class DigitalTwinLayerAssociationSchema(BaseModel):
    layer_id: int
    is_default: bool
    sort_order: int
    group_id: Optional[int] = None

    class Config:
        orm_mode = True

class DigitalTwinLayerAssociationCreate(BaseModel):
    layer_id: int
    is_default: bool
    sort_order: int
    group_id: Optional[int] = None

class DigitalTwinLayerRelationUpdate(BaseModel):
    layer_id: int
    is_default: bool
    sort_order: Optional[int] = None
    group_id: Optional[int] = None