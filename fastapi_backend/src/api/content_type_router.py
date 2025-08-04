from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.content_type_schema import (
    ContentTypeCreate,
    ContentTypeUpdate,
    ContentTypeResponse
)
import services.content_type_service as service

router = APIRouter(prefix="/content-types", tags=["Content Types"])

@router.get("/", response_model=list[ContentTypeResponse])
def get_all_content_types(db: Session = Depends(get_db)):
    return service.get_all_content_types(db)

@router.get("/{content_type_id}", response_model=ContentTypeResponse)
def get_content_type(content_type_id: int, db: Session = Depends(get_db)):
    content_type = service.get_content_type(db, content_type_id)
    if not content_type:
        raise HTTPException(status_code=404, detail="Content type not found")
    return content_type

@router.get("/name/{name}", response_model=ContentTypeResponse)
def get_content_type_by_name(name: str, db: Session = Depends(get_db)):
    content_type = service.get_content_type_by_name(db, name)
    if not content_type:
        raise HTTPException(status_code=404, detail="Content type not found")
    return content_type

@router.post("/", response_model=ContentTypeResponse)
def create_content_type(data: ContentTypeCreate, db: Session = Depends(get_db)):
    return service.create_content_type(db, data)

@router.put("/{content_type_id}", response_model=ContentTypeResponse)
def update_content_type(content_type_id: int, data: ContentTypeUpdate, db: Session = Depends(get_db)):
    updated = service.update_content_type(db, content_type_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Content type not found")
    return updated

@router.delete("/{content_type_id}")
def delete_content_type(content_type_id: int, db: Session = Depends(get_db)):
    deleted = service.delete_content_type(db, content_type_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Content type not found")
    return {"detail": "Deleted"}
