from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import get_db
import services.digital_twin_service as service
import services.viewer_service as viewer_service
import services.digital_twin_layer_relation_service as layer_service
import services.digital_twin_group_relation_service as group_service
import services.digital_twin_tool_relation_service as tool_service
import services.digital_twin_bookmark_relation_service as bookmark_service
import services.digital_twin_project_relation_service as project_service
import services.digital_twin_story_relation_service as story_service
import services.digital_twin_terrain_provider_relation_service as terrain_provider_service
import services.digital_twin_cesium_config_service as cesium_config_service
from schemas.digital_twin_schema import (
    DigitalTwinCreate,
    DigitalTwinUpdate,
    DigitalTwinResponse,
    DigitalTwinListResponse,
    BulkAssociationsPayload,
    PaginatedDigitalTwinResponse
)
from schemas.viewer_schema import (
    ViewerCreate,
    ViewerUpdate,
    ViewerResponse
)

from schemas.digital_twin_tool_association_schema import (
    DigitalTwinToolBulkOperation
)
from typing import Dict, Any
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/digital-twins", tags=["Digital Twins"])

@router.get("/", response_model=list[DigitalTwinListResponse])
def read_all_digital_twins(db: Session = Depends(get_db)):
    return service.list_digital_twins(db)

@router.get("/search", response_model=PaginatedDigitalTwinResponse)
def get_digital_twins_search(
    db: Session = Depends(get_db),
    search: str | None = Query(None, description="Search term"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_column: str = Query("name", description="Sort column"),
    sort_direction: str = Query("asc", description="Sort direction: asc or desc")
):
    results, total = service.get_digital_twins_filtered_paginated(
        db,
        search or "",
        page,
        page_size,
        sort_column,
        sort_direction
    )
    results = [DigitalTwinListResponse.model_validate(twin, from_attributes=True) for twin in results]
    return PaginatedDigitalTwinResponse(
        results=results,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{digital_twin_id}", response_model=DigitalTwinResponse)
def read_digital_twin(digital_twin_id: int, db: Session = Depends(get_db)):
    twin = service.get_digital_twin(digital_twin_id, db)
    if not twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    return twin

@router.post("/", response_model=DigitalTwinResponse)
def create_digital_twin(data: DigitalTwinCreate, db: Session = Depends(get_db)):
    try:
        return service.create_digital_twin(data, db)
    except IntegrityError as e:
        # Check for unique constraint violation
        if 'unique constraint' in str(e).lower() or 'duplicate key' in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail="Deze naam is al in gebruik. Kies een andere naam."
            )
        raise

@router.put("/{digital_twin_id}", response_model=DigitalTwinResponse)
def update_digital_twin(digital_twin_id: int, data: DigitalTwinUpdate, db: Session = Depends(get_db)):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    try:
        return service.update_digital_twin(db_twin, data, db)
    except IntegrityError as e:
        # Check for unique constraint violation
        if 'unique constraint' in str(e).lower() or 'duplicate key' in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail="Deze naam is al in gebruik. Kies een andere naam."
            )
        raise

@router.delete("/{digital_twin_id}", status_code=204)
def delete_digital_twin(digital_twin_id: int, db: Session = Depends(get_db)):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    service.delete_digital_twin(db_twin, db)

# Viewer routes
@router.get("/{digital_twin_id}/viewer", response_model=ViewerResponse)
def get_viewer(digital_twin_id: int, db: Session = Depends(get_db)):
    viewer = viewer_service.get_viewer_by_digital_twin_id(digital_twin_id, db)
    if not viewer:
        raise HTTPException(status_code=404, detail="Viewer not found")
    return viewer

@router.post("/{digital_twin_id}/viewer", response_model=ViewerResponse)
def create_viewer(digital_twin_id: int, viewer: ViewerCreate, db: Session = Depends(get_db)):
    return viewer_service.create_viewer_with_digital_twin_id(viewer, digital_twin_id, db)

@router.put("/{digital_twin_id}/viewer", response_model=ViewerResponse)
def update_viewer(digital_twin_id: int, viewer_update: ViewerUpdate, db: Session = Depends(get_db)):
    updated = viewer_service.update_viewer_by_digital_twin_id(digital_twin_id, viewer_update, db)
    if not updated:
        raise HTTPException(status_code=404, detail="Viewer not found")
    return updated

@router.delete("/{digital_twin_id}/viewer", status_code=204)
def delete_viewer(digital_twin_id: int, db: Session = Depends(get_db)):
    success = viewer_service.delete_viewer_by_digital_twin_id(digital_twin_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Viewer not found")

# Layer junction table bulk edit
@router.put("/{digital_twin_id}/associations/bulk")
def bulk_modify_layer_associations(
    digital_twin_id: int,
    payload: BulkAssociationsPayload,
    db: Session = Depends(get_db)
):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")

    layer_results = layer_service.handle_bulk_layer_operations(
        digital_twin_id, payload.layer_payload.operations, db
    )
    group_results = group_service.handle_bulk_group_operations(
        digital_twin_id, payload.group_payload.operations, db
    )
    
    return {"layers": layer_results, "groups": group_results}
    
# Tools junction table bulk routes
@router.put("/{digital_twin_id}/tools/bulk")
def bulk_modify_tool_associations(
    digital_twin_id: int,
    payload: DigitalTwinToolBulkOperation,
    db: Session = Depends(get_db)
):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")

    results = tool_service.handle_bulk_tool_operations(
        digital_twin_id, payload.operations, db
    )
    return {"tools": results}

# Bookmark associations
@router.put("/{digital_twin_id}/bookmarks/bulk")
def bulk_modify_bookmark_associations(
    digital_twin_id: int,
    payload: DigitalTwinToolBulkOperation,
    db: Session = Depends(get_db)
):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")

    results = bookmark_service.handle_bulk_bookmark_operations(
        digital_twin_id, payload.operations, db
    )
    return {"bookmarks": results}

@router.get("/{digital_twin_id}/bookmarks")
def get_digital_twin_bookmarks(digital_twin_id: int, db: Session = Depends(get_db)):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    
    return bookmark_service.get_digital_twin_bookmarks(digital_twin_id, db)

# Project associations
@router.put("/{digital_twin_id}/projects/bulk")
def bulk_modify_project_associations(
    digital_twin_id: int,
    payload: DigitalTwinToolBulkOperation,
    db: Session = Depends(get_db)
):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")

    results = project_service.handle_bulk_project_operations(
        digital_twin_id, payload.operations, db
    )
    return {"projects": results}

@router.get("/{digital_twin_id}/projects")
def get_digital_twin_projects(digital_twin_id: int, db: Session = Depends(get_db)):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    
    return project_service.get_digital_twin_projects(digital_twin_id, db)

# Story associations
@router.put("/{digital_twin_id}/stories/bulk")
def bulk_modify_story_associations(
    digital_twin_id: int,
    payload: DigitalTwinToolBulkOperation,
    db: Session = Depends(get_db)
):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")

    results = story_service.handle_bulk_story_operations(
        digital_twin_id, payload.operations, db
    )
    return {"stories": results}

@router.get("/{digital_twin_id}/stories")
def get_digital_twin_stories(digital_twin_id: int, db: Session = Depends(get_db)):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    
    return story_service.get_digital_twin_stories(digital_twin_id, db)

# Terrain Provider associations
@router.put("/{digital_twin_id}/terrain-providers/bulk")
def bulk_modify_terrain_provider_associations(
    digital_twin_id: int,
    payload: DigitalTwinToolBulkOperation,
    db: Session = Depends(get_db)
):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")

    results = terrain_provider_service.handle_bulk_terrain_provider_operations(
        digital_twin_id, payload.operations, db
    )
    return {"terrain_providers": results}

@router.get("/{digital_twin_id}/terrain-providers")
def get_digital_twin_terrain_providers(digital_twin_id: int, db: Session = Depends(get_db)):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    
    return terrain_provider_service.get_digital_twin_terrain_providers(digital_twin_id, db)

# Cesium tool configuration
@router.get("/{digital_twin_id}/cesium/config")
def get_cesium_configuration(digital_twin_id: int, db: Session = Depends(get_db)):
    """Get Cesium tool configuration for a digital twin"""
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    
    config = cesium_config_service.get_cesium_configuration(digital_twin_id, db)
    return {"config": config}

@router.put("/{digital_twin_id}/cesium/config")
def update_cesium_configuration(
    digital_twin_id: int, 
    config: Dict[str, Any], 
    db: Session = Depends(get_db)
):
    """Update Cesium tool configuration for a digital twin"""
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    
    cesium_config_service.update_cesium_configuration(digital_twin_id, config, db)
    return {"message": "Configuration updated successfully"}

@router.delete("/{digital_twin_id}/cesium/config")
def delete_cesium_configuration(digital_twin_id: int, db: Session = Depends(get_db)):
    """Delete Cesium tool configuration for a digital twin"""
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    
    cesium_config_service.delete_cesium_configuration(digital_twin_id, db)
    return {"message": "Configuration deleted successfully"}