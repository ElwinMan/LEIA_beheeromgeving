from pydantic import BaseModel
from typing import List, Literal

class DigitalTwinToolAssociationSchema(BaseModel):
    tool_id: int

    class Config:
        orm_mode = True

class DigitalTwinToolBulkItem(BaseModel):
    tool_id: int
    action: Literal["create", "delete"]

class DigitalTwinToolBulkOperation(BaseModel):
    operations: List[DigitalTwinToolBulkItem]