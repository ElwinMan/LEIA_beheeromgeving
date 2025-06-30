from pydantic import BaseModel, model_validator
from typing import Optional, Literal, List

class GroupBase(BaseModel):
    title: str
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None

class GroupCreate(GroupBase):
    digital_twin_id: int

class GroupUpdate(BaseModel):
    title: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None

class GroupResponse(BaseModel):
    id: int
    title: str
    parent_id: Optional[int] = None
    sort_order: int = 0

    class Config:
        orm_mode = True

class DigitalTwinGroupBulkItem(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = 0
    action: Literal['create', 'update', 'delete']

    @model_validator(mode="before")
    @classmethod
    def check_id_requirement(cls, data):
        action = data.get("action")
        id_ = data.get("id")

        if action in ("update", "delete") and id_ is None:
            raise ValueError(f"'id' is required for '{action}' action")

        return data

class DigitalTwinGroupBulkOperation(BaseModel):
    operations: List[DigitalTwinGroupBulkItem]