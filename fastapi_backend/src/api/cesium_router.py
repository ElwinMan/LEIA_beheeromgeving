from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
import services.cesium_service as service
from schemas.cesium_schema import (
    CesiumCreate,
    CesiumUpdate,
    CesiumResponse,
)

router = APIRouter(prefix="/cesiums", tags=["Cesium"])

@router.get("/", response_model=list[CesiumResponse])
def get_all_cesiums(db: Session = Depends(get_db)):
    return service.get_all_cesiums(db)

@router.get("/{cesium_id}", response_model=CesiumResponse)
def get_cesium(cesium_id: int, db: Session = Depends(get_db)):
    cesium = service.get_cesium(db, cesium_id)
    if not cesium:
        raise HTTPException(status_code=404, detail="Cesium not found")
    return cesium

@router.post("/", response_model=CesiumResponse)
def create_cesium(data: CesiumCreate, db: Session = Depends(get_db)):
    return service.create_cesium(db, data)

@router.put("/{cesium_id}", response_model=CesiumResponse)
def update_cesium(cesium_id: int, data: CesiumUpdate, db: Session = Depends(get_db)):
    updated = service.update_cesium(db, cesium_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Cesium not found")
    return updated

@router.delete("/{cesium_id}")
def delete_cesium(cesium_id: int, db: Session = Depends(get_db)):
    deleted = service.delete_cesium(db, cesium_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cesium not found")
    return {"detail": "Deleted"}