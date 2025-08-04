from pydantic import BaseModel
from typing import List

class ContentTypeBase(BaseModel):
    name: str
    table_name: str

class ContentTypeCreate(ContentTypeBase):
    pass

class ContentTypeUpdate(BaseModel):
    name: str = None
    table_name: str = None

class ContentTypeResponse(ContentTypeBase):
    id: int

    class Config:
        orm_mode = True

class PaginatedContentTypesResponse(BaseModel):
    results: List[ContentTypeResponse]
    total: int
    page: int
    page_size: int
