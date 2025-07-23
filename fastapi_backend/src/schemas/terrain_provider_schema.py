from pydantic import BaseModel
from typing import Optional, List

class TerrainProviderBase(BaseModel):
    title: str
    url: str
    vertexNormals: Optional[bool] = None

class TerrainProviderCreate(TerrainProviderBase):
    pass

class TerrainProviderUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    vertexNormals: Optional[bool] = None

class TerrainProviderResponse(TerrainProviderBase):
    id: int

    class Config:
        orm_mode = True

class PaginatedTerrainProvidersResponse(BaseModel):
    results: List[TerrainProviderResponse]
    total: int
    page: int
    page_size: int