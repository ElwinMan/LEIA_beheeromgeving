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