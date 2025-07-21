from sqlalchemy.orm import Session
import repositories.bookmark_repository as repo
from models.tool_associations import Bookmark
from schemas.bookmark_schema import (
    BookmarkCreate,
    BookmarkUpdate,
)

def get_bookmark(db: Session, bookmark_id: int) -> Bookmark | None:
    return repo.get_by_id(db, bookmark_id)

def get_all_bookmarks(db: Session) -> list[Bookmark]:
    return repo.get_all(db)

def create_bookmark(db: Session, data: BookmarkCreate) -> Bookmark:
    bookmark = Bookmark(**data.dict())
    return repo.create(db, bookmark)

def update_bookmark(db: Session, bookmark_id: int, updates: BookmarkUpdate) -> Bookmark | None:
    bookmark = repo.get_by_id(db, bookmark_id)
    if not bookmark:
        return None
    return repo.update(db, bookmark, updates.dict(exclude_unset=True))

def delete_bookmark(db: Session, bookmark_id: int) -> bool:
    return repo.delete(db, bookmark_id)