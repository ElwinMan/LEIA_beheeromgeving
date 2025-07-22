from sqlalchemy.orm import Session
from models.layer import Layer
from models.associations import DigitalTwinLayerAssociation
from models.digital_twin import DigitalTwin
from typing import Dict, Any

def get_layer_by_id(db: Session, layer_id: int):
    return db.query(Layer).filter(Layer.id == layer_id).first()

def get_layers_by_ids(db: Session, layer_ids: list[int]):
    return db.query(Layer).filter(Layer.id.in_(layer_ids)).all()

def get_all_layers(db: Session):
    return db.query(Layer).all()

def insert_layer(db: Session, layer: Layer) -> Layer:
    db.add(layer)
    db.commit()
    db.refresh(layer)
    return layer

def update_layer(db: Session, layer: Layer, updates: dict):
    for key, value in updates.items():
        setattr(layer, key, value)
    db.commit()
    db.refresh(layer)
    return layer

def delete_layer(db: Session, layer: Layer):
    db.delete(layer)
    db.commit()

def get_digital_twins_for_layer(db: Session, layer_id: int):
    associations = db.query(DigitalTwinLayerAssociation).filter_by(layer_id=layer_id).all()
    twin_ids = [assoc.digital_twin_id for assoc in associations]
    if not twin_ids:
        return []
    twins = db.query(DigitalTwin).filter(DigitalTwin.id.in_(twin_ids)).all()
    return twins