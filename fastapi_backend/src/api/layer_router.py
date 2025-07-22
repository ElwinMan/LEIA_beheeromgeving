from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.layer_schema import LayerCreate, LayerUpdate, LayerResponse
from schemas.digital_twin_schema import DigitalTwinSummary
import services.layer_service as service

router = APIRouter(prefix="/layers", tags=["Layers"])

@router.get("/", response_model=list[LayerResponse])
def get_layers(db: Session = Depends(get_db)):
    return service.list_layers(db)

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