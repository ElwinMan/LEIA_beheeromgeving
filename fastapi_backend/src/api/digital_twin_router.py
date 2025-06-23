from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
import services.digital_twin_service as service
import services.viewer_service as viewer_service
import services.digital_twin_layer_relation_service as relation_service
import services.digital_twin_tool_relation_service as tool_service
from schemas.digital_twin_schema import (
    DigitalTwinCreate,
    DigitalTwinUpdate,
    DigitalTwinResponse,
    DigitalTwinListResponse
)
from schemas.viewer_schema import (
    ViewerCreate,
    ViewerUpdate,
    ViewerResponse
)
from schemas.digital_twin_layer_association_schema import (
    DigitalTwinLayerAssociationCreate,
    DigitalTwinLayerRelationUpdate
)
from schemas.digital_twin_tool_association_schema import (
    DigitalTwinToolAssociationCreate
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

# Relation junction table routes for adding layers, groups and sorting order
@router.post("/{digital_twin_id}/layer")
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

@router.put("/{digital_twin_id}/layer/{layer_id}")
def update_relation_to_digital_twin(
    digital_twin_id: int,
    layer_id: int,
    update_data: DigitalTwinLayerRelationUpdate,
    db: Session = Depends(get_db)
):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")

    updated = relation_service.update_relation(digital_twin_id, layer_id, update_data, db)
    if not updated:
        raise HTTPException(status_code=404, detail="Layer relation not found")

    return {"message": "Relation updated"}

@router.delete("/{digital_twin_id}/layer/{layer_id}", status_code=204)
def delete_relation_from_digital_twin(
    digital_twin_id: int,
    layer_id: int,
    db: Session = Depends(get_db)
):
    deleted = relation_service.delete_relation(digital_twin_id, layer_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Relation not found")
    
# Tool junction table routes
@router.post("/{digital_twin_id}/tool")
def add_tool_to_digital_twin(
    digital_twin_id: int,
    tool_data: DigitalTwinToolAssociationCreate,
    db: Session = Depends(get_db)
):
    db_twin = service.get_digital_twin(digital_twin_id, db)
    if not db_twin:
        raise HTTPException(status_code=404, detail="Digital twin not found")

    tool_service.add_tool_association(digital_twin_id, tool_data, db)
    return {"message": "Tool association created"}

@router.delete("/{digital_twin_id}/tool/{tool_id}", status_code=204)
def delete_tool_from_digital_twin(
    digital_twin_id: int,
    tool_id: int,
    db: Session = Depends(get_db)
):
    deleted = tool_service.delete_relation(digital_twin_id, tool_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Relation not found")