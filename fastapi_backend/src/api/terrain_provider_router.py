from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
import services.terrain_provider_service as service
from schemas.terrain_provider_schema import (
    TerrainProviderCreate,
    TerrainProviderUpdate,
    TerrainProviderResponse,
)

router = APIRouter(prefix="/terrain-providers", tags=["TerrainProvider"])

@router.get("/", response_model=list[TerrainProviderResponse])
def get_all_terrain_providers(db: Session = Depends(get_db)):
    return service.get_all_terrain_providers(db)

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