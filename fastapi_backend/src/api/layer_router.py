from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.layer_schema import LayerCreate, LayerUpdate, LayerResponse, PaginatedLayersResponse
from schemas.digital_twin_schema import DigitalTwinSummary
import services.layer_service as service

router = APIRouter(prefix="/layers", tags=["Layers"])

@router.get("/", response_model=list[LayerResponse])
def get_layers(db: Session = Depends(get_db)):
    return service.list_layers(db)

@router.get("/search", response_model=PaginatedLayersResponse)
def get_layers_search(
    db: Session = Depends(get_db),
    search: str | None = Query(None, description="Search term"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_column: str = Query("title", description="Sort column"),
    sort_direction: str = Query("asc", description="Sort direction: asc or desc"),
    is_background: bool | None = Query(None, description="Filter by isBackground")
):
    results, total = service.get_layers_filtered_paginated(
        db,
        search or "",
        page,
        page_size,
        sort_column,
        sort_direction,
        is_background
    )
    results = [LayerResponse.model_validate(layer, from_attributes=True) for layer in results]
    return PaginatedLayersResponse(
        results=results,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{layer_id}", response_model=LayerResponse)
def read_layer(layer_id: int, db: Session = Depends(get_db)):
    layer = service.get_layer(layer_id, db)
    if not layer:
        raise HTTPException(status_code=404, detail="Layer not found")
    return layer

@router.post("/", response_model=LayerResponse)
def create_layer(layer: LayerCreate, db: Session = Depends(get_db)):
    return service.create_layer(layer, db)

@router.put("/{layer_id}", response_model=LayerResponse)
def update_layer(layer_id: int, layer_update: LayerUpdate, db: Session = Depends(get_db)):
    existing_layer = service.get_layer(layer_id, db)
    if not existing_layer:
        raise HTTPException(status_code=404, detail="Layer not found")

    return service.update_layer(existing_layer, layer_update, db)


@router.delete("/{layer_id}", status_code=204)
def delete_layer(layer_id: int, db: Session = Depends(get_db)):
    existing_layer = service.get_layer(layer_id, db)
    if not existing_layer:
        raise HTTPException(status_code=404, detail="Layer not found")

    service.delete_layer(existing_layer, db)

@router.get("/{layer_id}/digital-twins", response_model=list[DigitalTwinSummary])
def get_digital_twins_for_layer(layer_id: int, db: Session = Depends(get_db)):
    twins = service.get_digital_twins_for_layer(layer_id, db)
    return twins