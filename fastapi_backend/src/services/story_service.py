from sqlalchemy.orm import Session
import repositories.story_repository as repo
from models.tool_associations import Story
from schemas.story_schema import (
    StoryCreate,
    StoryUpdate,
)

def get_story(db: Session, story_id: int) -> Story | None:
    return repo.get_by_id(db, story_id)

def get_all_stories(db: Session) -> list[Story]:
    return repo.get_all(db)

def create_story(db: Session, data: StoryCreate) -> Story:
    story = Story(**data.dict())
    return repo.create(db, story)

def update_story(db: Session, story_id: int, updates: StoryUpdate) -> Story | None:
    story = repo.get_by_id(db, story_id)
    if not story:
        return None
    return repo.update(db, story, updates.dict(exclude_unset=True))

def delete_story(db: Session, story_id: int) -> bool:
    return repo.delete(db, story_id)

def get_stories_filtered_paginated(
    db: Session,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    sort_column: str = "name",
    sort_direction: str = "asc"
):
    return repo.get_filtered_paginated(
        db,
        search,
        page,
        page_size,
        sort_column,
        sort_direction
    )