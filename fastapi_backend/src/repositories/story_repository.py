from sqlalchemy.orm import Session
from models.tool_associations import Story

def get_by_id(db: Session, story_id: int):
    return db.query(Story).filter_by(id=story_id).first()

def get_all(db: Session):
    return db.query(Story).all()

def create(db: Session, story: Story):
    db.add(story)
    db.commit()
    db.refresh(story)
    return story

def update(db: Session, story: Story, updates: dict):
    for key, value in updates.items():
        setattr(story, key, value)
    db.commit()
    db.refresh(story)
    return story

def delete(db: Session, story_id: int):
    story = db.query(Story).filter_by(id=story_id).first()
    if story:
        db.delete(story)
        db.commit()
    return story