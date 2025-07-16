from sqlalchemy.orm import Session
import repositories.story_repository as repository
from models.tool_associations import Stories
from schemas.story_schema import (
    StoryCreate,
    StoryUpdate,
)

def get_story(db: Session, story_id: int) -> Stories | None:
    return repository.get_by_id(db, story_id)

def get_all_stories(db: Session) -> list[Stories]:
    return repository.get_all(db)

def create_story(db: Session, data: StoryCreate) -> Stories:
    story = Stories(**data.dict())
    return repository.create(db, story)

def update_story(db: Session, story_id: int, updates: StoryUpdate) -> Stories | None:
    story = repository.get_by_id(db, story_id)
    if not story:
        return None
    return repository.update(db, story, updates.dict(exclude_unset=True))

def delete_story(db: Session, story_id: int) -> bool:
    return repository.delete(db, story_id)