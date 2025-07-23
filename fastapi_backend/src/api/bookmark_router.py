from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import get_db
import services.bookmark_service as service
from schemas.bookmark_schema import (
    BookmarkCreate,
    BookmarkUpdate,
    BookmarkResponse,
    PaginatedBookmarksResponse
)

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])

@router.get("/", response_model=list[BookmarkResponse])
def get_all_bookmark(db: Session = Depends(get_db)):
    return service.get_all_bookmarks(db)

@router.get("/search", response_model=PaginatedBookmarksResponse)
def get_bookmarks_search(
    db: Session = Depends(get_db),
    search: str | None = Query(None, description="Search term"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_column: str = Query("title", description="Sort column"),
    sort_direction: str = Query("asc", description="Sort direction: asc or desc")
):
    params = {}
    if search:
        params['search'] = search
    results, total = service.get_bookmarks_filtered_paginated(
        db,
        **params,
        page=page,
        page_size=page_size,
        sort_column=sort_column,
        sort_direction=sort_direction
    )
    results = [BookmarkResponse.model_validate(b, from_attributes=True) for b in results]
    return PaginatedBookmarksResponse(
        results=results,
        total=total,
        page=page,
        page_size=page_size
    )

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