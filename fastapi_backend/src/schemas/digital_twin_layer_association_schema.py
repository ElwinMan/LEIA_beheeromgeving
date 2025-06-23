from pydantic import BaseModel
from typing import Optional

class DigitalTwinLayerAssociationSchema(BaseModel):
    layer_id: int
    sort_order: int
    group_id: Optional[int] = None

    class Config:
        orm_mode = True

class DigitalTwinLayerAssociationCreate(BaseModel):
    layer_id: int
    sort_order: int
    group_id: Optional[int] = None

class DigitalTwinLayerRelationUpdate(BaseModel):
    layer_id: int
    sort_order: Optional[int] = None
    group_id: Optional[int] = None