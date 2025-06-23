from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.group_schema import GroupCreate, GroupUpdate, GroupResponse
import services.group_service as service

router = APIRouter(prefix="/digital_twins/{digital_twin_id}/groups", tags=["Digital Twin Groups"])

@router.get("/", response_model=list[GroupResponse])
def list_groups(digital_twin_id: int, db: Session = Depends(get_db)):
    return service.list_groups(digital_twin_id, db)

@router.get("/{group_id}", response_model=GroupResponse)
def get_group(digital_twin_id: int, group_id: int, db: Session = Depends(get_db)):
    group = service.get_group(group_id, db)
    if not group or group.digital_twin_id != digital_twin_id:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.post("/", response_model=GroupResponse)
def create_group(digital_twin_id: int, group_data: GroupCreate, db: Session = Depends(get_db)):
    return service.create_group(digital_twin_id, group_data, db)

@router.put("/{group_id}", response_model=GroupResponse)
def update_group(digital_twin_id: int, group_id: int, update: GroupUpdate, db: Session = Depends(get_db)):
    updated = service.update_group(digital_twin_id, group_id, update, db)
    if not updated:
        raise HTTPException(status_code=404, detail="Group not found or does not belong to the specified digital twin")
    return updated

@router.delete("/{group_id}")
def delete_group(digital_twin_id: int, group_id: int, db: Session = Depends(get_db)):
    success = service.delete_group(digital_twin_id, group_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Group not found or does not belong to the specified digital twin")
    return {"detail": "Group deleted"}