from pydantic import BaseModel
from typing import List, Literal, Optional

class DigitalTwinToolAssociationSchema(BaseModel):
    id: int
    tool_id: int
    content_type_id: Optional[int] = None
    content_id: Optional[int] = None
    sort_order: int
    is_default: Optional[bool] = False
    content: Optional[dict] = None

    class Config:
        from_attributes = True

class DigitalTwinToolBulkItem(BaseModel):
    tool_id: int
    content_type_id: Optional[int] = None
    content_id: Optional[int] = None
    sort_order: Optional[int] = 0
    is_default: Optional[bool] = False
    content: Optional[dict] = None
    action: Literal["create", "update", "delete"]

class DigitalTwinToolBulkOperation(BaseModel):
    operations: List[DigitalTwinToolBulkItem]