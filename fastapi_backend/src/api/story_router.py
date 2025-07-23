from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import get_db
import services.story_service as service
from schemas.story_schema import (
    PaginatedStoriesResponse,
    StoryCreate,
    StoryUpdate,
    StoryResponse,
)

router = APIRouter(prefix="/stories", tags=["Stories"])

@router.get("/", response_model=list[StoryResponse])
def get_all_stories(db: Session = Depends(get_db)):
    return service.get_all_stories(db)

@router.get("/search", response_model=PaginatedStoriesResponse)
def get_stories_search(
    db: Session = Depends(get_db),
    search: str | None = Query(None, description="Search term"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_column: str = Query("name", description="Sort column"),
    sort_direction: str = Query("asc", description="Sort direction: asc or desc")
):
    results, total = service.get_stories_filtered_paginated(
        db,
        search or "",
        page,
        page_size,
        sort_column,
        sort_direction
    )
    results = [StoryResponse.model_validate(story, from_attributes=True) for story in results]
    return PaginatedStoriesResponse(
        results=results,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{story_id}", response_model=StoryResponse)
def get_story(story_id: int, db: Session = Depends(get_db)):
    story = service.get_story(db, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.post("/", response_model=StoryResponse)
def create_story(data: StoryCreate, db: Session = Depends(get_db)):
    return service.create_story(db, data)

@router.put("/{story_id}", response_model=StoryResponse)
def update_story(story_id: int, data: StoryUpdate, db: Session = Depends(get_db)):
    updated = service.update_story(db, story_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Story not found")
    return updated

@router.delete("/{story_id}")
def delete_story(story_id: int, db: Session = Depends(get_db)):
    deleted = service.delete_story(db, story_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Story not found")
    return {"detail": "Deleted"}