from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
import services.digital_twin_service as service
import services.digital_twin_relation_service as relation_service
from schemas.digital_twin_schema import (
    DigitalTwinCreate,
    DigitalTwinUpdate,
    DigitalTwinResponse,
    DigitalTwinListResponse
)
from schemas.digital_twin_layer_association_schema import (
    DigitalTwinLayerAssociationCreate,
    DigitalTwinRelationUpdate
)

router = APIRouter(prefix="/digital_twins", tags=["Digital Twins"])

@router.get("/", response_model=list[DigitalTwinListResponse])
def read_all_digital_twins(db: Session = Depends(get_db)):
    return service.list_digital_twins(db)

@router.get("/{digital_twin_id}", response_model=DigitalTwinResponse)
def read_digital_twin(digital_twin_id: int, db: Session = Depends(get_db)):
    twin = service.get_digital_twin(digital_twin_id, db)
    if not twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    return twin

@router.post("/", response_model=DigitalTwinResponse)
def create_digital_twin(data: DigitalTwinCreate, db: Session = Depends(get_db)):
    return service.create_digital_twin(data, db)

@router.put("/{digital_twin_id}", response_model=DigitalTwinResponse)
def update_digital_twin(digital_twin_id: int, data: DigitalTwinUpdate, db: Session = Depends(get_db)):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    return service.update_digital_twin(db_twin, data, db)

@router.delete("/{digital_twin_id}", status_code=204)
def delete_digital_twin(digital_twin_id: int, db: Session = Depends(get_db)):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")
    service.delete_digital_twin(db_twin, db)

# Relation junction table routes for adding layers, groups and sorting order
@router.post("/{digital_twin_id}/relation")
def add_layer_to_digital_twin(
    digital_twin_id: int,
    layer_data: DigitalTwinLayerAssociationCreate,
    db: Session = Depends(get_db)
):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")

    relation_service.add_layer_association(digital_twin_id, layer_data, db)
    return {"message": "Layer association created"}

@router.put("/{digital_twin_id}/relation/{layer_id}")
def update_relation_to_digital_twin(
    digital_twin_id: int,
    layer_id: int,
    update_data: DigitalTwinRelationUpdate,
    db: Session = Depends(get_db)
):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")

    updated = relation_service.update_relation(digital_twin_id, layer_id, update_data, db)
    if not updated:
        raise HTTPException(status_code=404, detail="Layer relation not found")

    return {"message": "Relation updated"}

@router.delete("/{digital_twin_id}/relation/{layer_id}", status_code=204)
def delete_relation_from_digital_twin(
    digital_twin_id: int,
    layer_id: int,
    db: Session = Depends(get_db)
):
    deleted = relation_service.delete_relation(digital_twin_id, layer_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Relation not found")