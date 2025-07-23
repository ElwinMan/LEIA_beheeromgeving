from sqlalchemy.orm import Session
from models.tool_associations import Bookmark

def get_by_id(db: Session, bookmark_id: int):
    return db.query(Bookmark).filter_by(id=bookmark_id).first()

def get_all(db: Session):
    return db.query(Bookmark).all()

def create(db: Session, bookmark: Bookmark):
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark

def update(db: Session, bookmark: Bookmark, updates: dict):
    for key, value in updates.items():
        setattr(bookmark, key, value)
    db.commit()
    db.refresh(bookmark)
    return bookmark

def delete(db: Session, bookmark_id: int):
    bookmark = db.query(Bookmark).filter_by(id=bookmark_id).first()
    if bookmark:
        db.delete(bookmark)
        db.commit()
    return bookmark

def get_filtered_paginated(
    db: Session,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    sort_column: str = "title",
    sort_direction: str = "asc"
):
    query = db.query(Bookmark)
    if search:
        search_lower = f"%{search.lower()}%"
        query = query.filter(
            (Bookmark.title.ilike(search_lower)) |
            (Bookmark.description.ilike(search_lower))
        )
    # Sorting
    if sort_column in ["title", "description", "id"]:
        sort_attr = getattr(Bookmark, sort_column)
        if sort_direction == "desc":
            sort_attr = sort_attr.desc()
        query = query.order_by(sort_attr)
    total = query.count()
    results = query.offset((page - 1) * page_size).limit(page_size).all()
    return results, total