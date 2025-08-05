from sqlalchemy.orm import Session
import repositories.bookmark_repository as repo
import repositories.digital_twin_tool_relation_repository as tool_relation_repo
import services.content_type_service as content_type_service
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
    # Check if the bookmark exists first
    bookmark = repo.get_by_id(db, bookmark_id)
    if not bookmark:
        return False
    
    try:
        # Get the bookmark content type
        bookmark_content_type = content_type_service.get_content_type_by_name(db, "bookmark")
        
        if bookmark_content_type:
            # Delete all digital_twin_tool_association records that reference this bookmark
            from models.associations import DigitalTwinToolAssociation
            associations = db.query(DigitalTwinToolAssociation).filter(
                DigitalTwinToolAssociation.content_type_id == bookmark_content_type.id,
                DigitalTwinToolAssociation.content_id == bookmark_id
            ).all()
            
            for assoc in associations:
                db.delete(assoc)
        
        # Delete the bookmark itself
        db.delete(bookmark)
        db.commit()
        return True
        
    except Exception:
        db.rollback()
        raise

def get_bookmarks_filtered_paginated(
    db: Session,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    sort_column: str = "title",
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