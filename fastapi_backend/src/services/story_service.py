from sqlalchemy.orm import Session
import repositories.story_repository as repository
from models.tool_associations import StoriesSnippets
from schemas.story_schema import (
    StorySnippetCreate,
    StorySnippetUpdate,
)

def get_snippet(db: Session, snippet_id: int) -> StoriesSnippets | None:
    return repository.get_by_id(db, snippet_id)

def get_all_snippets(db: Session) -> list[StoriesSnippets]:
    return repository.get_all(db)

def create_snippet(db: Session, data: StorySnippetCreate) -> StoriesSnippets:
    snippet = StoriesSnippets(**data.dict())
    return repository.create(db, snippet)

def update_snippet(db: Session, snippet_id: int, updates: StorySnippetUpdate) -> StoriesSnippets | None:
    snippet = repository.get_by_id(db, snippet_id)
    if not snippet:
        return None
    return repository.update(db, snippet, updates.dict(exclude_unset=True))

def delete_snippet(db: Session, snippet_id: int) -> bool:
    return repository.delete(db, snippet_id)