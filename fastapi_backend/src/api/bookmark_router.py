from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
import services.bookmark_service as service
from schemas.bookmark_schema import (
    BookmarkCreate,
    BookmarkUpdate,
    BookmarkResponse,
)

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])

@router.get("/", response_model=list[BookmarkResponse])
def get_all_bookmark(db: Session = Depends(get_db)):
    return service.get_all_bookmarks(db)

@router.get("/{bookmark_id}", response_model=BookmarkResponse)
def get_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    bookmark = service.get_bookmark(db, bookmark_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bookmark

@router.post("/", response_model=BookmarkResponse)
def create_bookmark(data: BookmarkCreate, db: Session = Depends(get_db)):
    return service.create_bookmark(db, data)

@router.put("/{bookmark_id}", response_model=BookmarkResponse)
def update_bookmark(bookmark_id: int, data: BookmarkUpdate, db: Session = Depends(get_db)):
    updated = service.update_bookmark(db, bookmark_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return updated

@router.delete("/{bookmark_id}")
def delete_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    deleted = service.delete_bookmark(db, bookmark_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return {"detail": "Deleted"}