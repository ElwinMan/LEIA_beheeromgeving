from sqlalchemy.orm import Session
from models.tool_associations import TerrainProvider

def get_by_id(db: Session, terrainProvider_id: int):
    return db.query(TerrainProvider).filter_by(id=terrainProvider_id).first()

def get_all(db: Session):
    return db.query(TerrainProvider).all()

def create(db: Session, terrainProvider: TerrainProvider):
    db.add(terrainProvider)
    db.commit()
    db.refresh(terrainProvider)
    return terrainProvider

def update(db: Session, terrainProvider: TerrainProvider, updates: dict):
    for key, value in updates.items():
        setattr(terrainProvider, key, value)
    db.commit()
    db.refresh(terrainProvider)
    return terrainProvider

def delete(db: Session, terrainProvider_id: int):
    terrainProvider = db.query(TerrainProvider).filter_by(id=terrainProvider_id).first()
    if terrainProvider:
        db.delete(terrainProvider)
        db.commit()
    return terrainProvider