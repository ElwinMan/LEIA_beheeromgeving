from sqlalchemy.orm import Session
import repositories.bookmark_repository as repository
from models.tool_associations import Bookmarks
from schemas.bookmark_schema import (
    BookmarkCreate,
    BookmarkUpdate,
)

def get_bookmark(db: Session, bookmark_id: int) -> Bookmarks | None:
    return repository.get_by_id(db, bookmark_id)

def get_all_bookmarks(db: Session) -> list[Bookmarks]:
    return repository.get_all(db)

def create_bookmark(db: Session, data: BookmarkCreate) -> Bookmarks:
    bookmark = Bookmarks(**data.dict())
    return repository.create(db, bookmark)

def update_bookmark(db: Session, bookmark_id: int, updates: BookmarkUpdate) -> Bookmarks | None:
    bookmark = repository.get_by_id(db, bookmark_id)
    if not bookmark:
        return None
    return repository.update(db, bookmark, updates.dict(exclude_unset=True))

def delete_bookmark(db: Session, bookmark_id: int) -> bool:
    return repository.delete(db, bookmark_id)