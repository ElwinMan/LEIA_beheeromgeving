from pydantic import BaseModel
from typing import Optional

class GroupBase(BaseModel):
    title: str
    digital_twin_id: int
    parent_id: Optional[int] = None
    sort_order: int = 0

class GroupCreate(GroupBase):
    pass

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
