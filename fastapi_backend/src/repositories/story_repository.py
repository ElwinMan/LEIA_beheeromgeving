from sqlalchemy.orm import Session
from models.tool_associations import StoriesSnippets

def get_by_id(db: Session, snippet_id: int):
    return db.query(StoriesSnippets).filter_by(id=snippet_id).first()

def get_all(db: Session):
    return db.query(StoriesSnippets).all()

def create(db: Session, snippet: StoriesSnippets):
    db.add(snippet)
    db.commit()
    db.refresh(snippet)
    return snippet

def update(db: Session, snippet: StoriesSnippets, updates: dict):
    for key, value in updates.items():
        setattr(snippet, key, value)
    db.commit()
    db.refresh(snippet)
    return snippet

def delete(db: Session, snippet_id: int):
    snippet = db.query(StoriesSnippets).filter_by(id=snippet_id).first()
    if snippet:
        db.delete(snippet)
        db.commit()
    return snippet