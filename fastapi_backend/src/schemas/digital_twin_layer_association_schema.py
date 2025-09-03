from pydantic import BaseModel
from typing import List, Literal, Optional

class DigitalTwinLayerAssociationSchema(BaseModel):
    layer_id: int
    is_default: bool
    sort_order: int
    group_id: Optional[int] = None
    content: Optional[dict] = None

    class Config:
        orm_mode = True

class DigitalTwinLayerBulkItem(BaseModel):
    layer_id: int
    action: Literal["create", "update", "delete"]
    is_default: Optional[bool] = None
    sort_order: Optional[int] = None
    group_id: Optional[int] = None
    content: Optional[dict] = None

class DigitalTwinLayerBulkOperation(BaseModel):
    operations: List[DigitalTwinLayerBulkItem]