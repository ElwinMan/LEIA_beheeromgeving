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

# New schema for terrain provider tool associations (with reference to actual terrain provider)
class TerrainProviderToolAssociationCreate(BaseModel):
    terrain_provider_id: int
    sort_order: Optional[int] = 0

class TerrainProviderToolAssociationResponse(BaseModel):
    id: int
    tool_id: int
    content_type_id: Optional[int] = None
    content_id: int  # This will be the terrain_provider_id
    sort_order: int
    # Include the actual terrain provider data
    terrain_provider: Optional[TerrainProviderResponse] = None

    class Config:
        orm_mode = True

class PaginatedTerrainProvidersResponse(BaseModel):
    results: List[TerrainProviderResponse]
    total: int
    page: int
    page_size: int