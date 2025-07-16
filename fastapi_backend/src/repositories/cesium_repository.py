from sqlalchemy.orm import Session
from models.tool_associations import Cesium

def get_by_id(db: Session, cesium_id: int):
    return db.query(Cesium).filter_by(id=cesium_id).first()

def get_all(db: Session):
    return db.query(Cesium).all()

def create(db: Session, cesium: Cesium):
    db.add(cesium)
    db.commit()
    db.refresh(cesium)
    return cesium

def update(db: Session, cesium: Cesium, updates: dict):
    for key, value in updates.items():
        setattr(cesium, key, value)
    db.commit()
    db.refresh(cesium)
    return cesium

def delete(db: Session, cesium_id: int):
    cesium = db.query(Cesium).filter_by(id=cesium_id).first()
    if cesium:
        db.delete(cesium)
        db.commit()
    return cesium