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

def get_filtered_paginated(
    db: Session,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    sort_column: str = "title",
    sort_direction: str = "asc",
    is_background: bool | None = None
):
    query = db.query(Layer)
    if search:
        search_lower = f"%{search.lower()}%"
        query = query.filter(
            (Layer.title.ilike(search_lower)) |
            (Layer.type.ilike(search_lower)) |
            (Layer.url.ilike(search_lower)) |
            (Layer.featureName.ilike(search_lower))
        )
    if is_background is not None:
        query = query.filter(Layer.isBackground == is_background)
    allowed_columns = ["title", "type", "url", "featureName", "id"]
    if sort_column in allowed_columns:
        sort_attr = getattr(Layer, sort_column)
        if sort_direction == "desc":
            sort_attr = sort_attr.desc()
        query = query.order_by(sort_attr)
    total = query.count()
    results = query.offset((page - 1) * page_size).limit(page_size).all()
    return results, total