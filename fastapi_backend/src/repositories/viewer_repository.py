from sqlalchemy.orm import Session
from models.viewer import Viewer
from typing import Optional, Dict, Any

def get_viewer_by_digital_twin_id(db: Session, digital_twin_id: int):
    return db.query(Viewer).filter(Viewer.digital_twin_id == digital_twin_id).first()

def insert_viewer(db: Session, viewer_data: Dict[str, Any]) -> Viewer:
    viewer = Viewer(**viewer_data)
    db.add(viewer)
    db.commit()
    db.refresh(viewer)
    return viewer

def update_viewer(db: Session, viewer, updates: dict):
    for key, value in updates.items():
        setattr(viewer, key, value)
    db.commit()
    db.refresh(viewer)
    return viewer

def delete_viewer(db: Session, viewer):
    db.delete(viewer)
    db.commit()