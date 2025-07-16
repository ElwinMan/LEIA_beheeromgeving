from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
import services.story_service as service
from schemas.story_schema import (
    StoryCreate,
    StoryUpdate,
    StoryResponse,
)

router = APIRouter(prefix="/stories", tags=["Stories"])

@router.get("/", response_model=list[StoryResponse])
def get_all_stories(db: Session = Depends(get_db)):
    return service.get_all_stories(db)

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