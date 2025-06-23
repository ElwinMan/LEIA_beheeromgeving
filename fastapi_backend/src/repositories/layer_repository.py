from sqlalchemy.orm import Session
from models.layer import Layer
from typing import Optional, Dict, Any

def get_layer_by_id(db: Session, layer_id: int):
    return db.query(Layer).filter(Layer.id == layer_id).first()

def get_all_layers(db: Session):
    return db.query(Layer).all()

def insert_layer(db: Session, layer_data: Dict[str, Any]) -> Layer:
    layer = Layer(**layer_data)
    db.add(layer)
    db.commit()
    db.refresh(layer)
    return layer

def update_layer(db: Session, layer, updates: dict):
    for key, value in updates.items():
        setattr(layer, key, value)
    db.commit()
    db.refresh(layer)
    return layer

def delete_layer(db: Session, layer):
    db.delete(layer)
    db.commit()