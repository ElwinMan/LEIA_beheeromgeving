from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import get_db
import services.terrain_provider_service as service
from schemas.terrain_provider_schema import (
    PaginatedTerrainProvidersResponse,
    TerrainProviderCreate,
    TerrainProviderUpdate,
    TerrainProviderResponse,
)

router = APIRouter(prefix="/terrain-providers", tags=["TerrainProvider"])

@router.get("/", response_model=list[TerrainProviderResponse])
def get_all_terrain_providers(db: Session = Depends(get_db)):
    return service.get_all_terrain_providers(db)

@router.get("/search", response_model=PaginatedTerrainProvidersResponse)
def get_terrain_providers_search(
    db: Session = Depends(get_db),
    search: str | None = Query(None, description="Search term"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_column: str = Query("title", description="Sort column"),
    sort_direction: str = Query("asc", description="Sort direction: asc or desc")
):
    results, total = service.get_terrain_providers_filtered_paginated(
        db,
        search or "",
        page,
        page_size,
        sort_column,
        sort_direction
    )
    results = [TerrainProviderResponse.model_validate(tp, from_attributes=True) for tp in results]
    return PaginatedTerrainProvidersResponse(
        results=results,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{terrain_provider_id}", response_model=TerrainProviderResponse)
def get_terrain_provider(terrain_provider_id: int, db: Session = Depends(get_db)):
    terrain_provider = service.get_terrain_provider(db, terrain_provider_id)
    if not terrain_provider:
        raise HTTPException(status_code=404, detail="TerrainProvider not found")
    return terrain_provider

@router.post("/", response_model=TerrainProviderResponse)
def create_terrain_provider(data: TerrainProviderCreate, db: Session = Depends(get_db)):
    return service.create_terrain_provider(db, data)

@router.put("/{terrain_provider_id}", response_model=TerrainProviderResponse)
def update_terrain_provider(terrain_provider_id: int, data: TerrainProviderUpdate, db: Session = Depends(get_db)):
    updated = service.update_terrain_provider(db, terrain_provider_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="TerrainProvider not found")
    return updated

@router.delete("/{terrain_provider_id}")
def delete_terrain_provider(terrain_provider_id: int, db: Session = Depends(get_db)):
    deleted = service.delete_terrain_provider(db, terrain_provider_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="TerrainProvider not found")
    return {"detail": "Deleted"}