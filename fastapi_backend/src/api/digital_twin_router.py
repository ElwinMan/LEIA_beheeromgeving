from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
import services.digital_twin_service as service
import services.viewer_service as viewer_service
import services.digital_twin_layer_relation_service as layer_service
import services.digital_twin_group_relation_service as group_service
import services.digital_twin_tool_relation_service as tool_service
from schemas.digital_twin_schema import (
    DigitalTwinCreate,
    DigitalTwinUpdate,
    DigitalTwinResponse,
    DigitalTwinListResponse,
    BulkAssociationsPayload
)
from schemas.viewer_schema import (
    ViewerCreate,
    ViewerUpdate,
    ViewerResponse
)
from schemas.digital_twin_layer_association_schema import (
    DigitalTwinLayerAssociationCreate,
    DigitalTwinLayerRelationUpdate,
)
from schemas.digital_twin_tool_association_schema import (
    DigitalTwinToolBulkOperation
)
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/digital-twins", tags=["Digital Twins"])

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