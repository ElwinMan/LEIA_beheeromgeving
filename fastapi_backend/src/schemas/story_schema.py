from pydantic import BaseModel
from typing import Optional, Any

class StoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    content: Optional[Any] = None

class StoryCreate(StoryBase):
    pass

class StoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[Any] = None

class StoryResponse(StoryBase):
    id: int

    class Config:
        orm_mode = True