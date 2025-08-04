from sqlalchemy.orm import Session
from models.content_type import ContentType

def get_by_id(db: Session, content_type_id: int):
    return db.query(ContentType).filter_by(id=content_type_id).first()

def get_by_name(db: Session, name: str):
    return db.query(ContentType).filter_by(name=name).first()

def get_all(db: Session):
    return db.query(ContentType).all()

def create(db: Session, content_type: ContentType):
    db.add(content_type)
    db.commit()
    db.refresh(content_type)
    return content_type

def update(db: Session, content_type: ContentType, updates: dict):
    for key, value in updates.items():
        setattr(content_type, key, value)
    db.commit()
    db.refresh(content_type)
    return content_type

def delete(db: Session, content_type_id: int):
    content_type = db.query(ContentType).filter_by(id=content_type_id).first()
    if content_type:
        db.delete(content_type)
        db.commit()
    return content_type
