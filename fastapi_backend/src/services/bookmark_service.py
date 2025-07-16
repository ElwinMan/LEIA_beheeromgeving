from sqlalchemy.orm import Session
import repositories.bookmark_repository as repository
from models.tool_associations import BookmarksSnippets
from schemas.bookmark_schema import (
    BookmarkSnippetCreate,
    BookmarkSnippetUpdate,
)

def get_snippet(db: Session, snippet_id: int) -> BookmarksSnippets | None:
    return repository.get_by_id(db, snippet_id)

def get_all_snippets(db: Session) -> list[BookmarksSnippets]:
    return repository.get_all(db)

def create_snippet(db: Session, data: BookmarkSnippetCreate) -> BookmarksSnippets:
    snippet = BookmarksSnippets(**data.dict())
    return repository.create(db, snippet)

def update_snippet(db: Session, snippet_id: int, updates: BookmarkSnippetUpdate) -> BookmarksSnippets | None:
    snippet = repository.get_by_id(db, snippet_id)
    if not snippet:
        return None
    return repository.update(db, snippet, updates.dict(exclude_unset=True))

def delete_snippet(db: Session, snippet_id: int) -> bool:
    return repository.delete(db, snippet_id)