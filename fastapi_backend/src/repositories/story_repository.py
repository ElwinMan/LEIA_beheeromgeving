from sqlalchemy.orm import Session
from models.tool_associations import Stories

def get_by_id(db: Session, story_id: int):
    return db.query(Stories).filter_by(id=story_id).first()

def get_all(db: Session):
    return db.query(Stories).all()

def create(db: Session, story: Stories):
    db.add(story)
    db.commit()
    db.refresh(story)
    return story

def update(db: Session, story: Stories, updates: dict):
    for key, value in updates.items():
        setattr(story, key, value)
    db.commit()
    db.refresh(story)
    return story

def delete(db: Session, story_id: int):
    story = db.query(Stories).filter_by(id=story_id).first()
    if story:
        db.delete(story)
        db.commit()
    return story