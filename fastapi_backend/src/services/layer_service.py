from sqlalchemy.orm import Session
from schemas.layer_schema import LayerCreate, LayerUpdate
import repositories.layer_repository as repo
from models.layer import Layer

def get_layer(layer_id: int, db: Session):
    return repo.get_layer_by_id(db, layer_id)

def list_layers(db: Session):
    return repo.get_all_layers(db)

def create_layer(layer_create: LayerCreate, db: Session):
    layer = Layer(**layer_create.dict())
    return repo.insert_layer(db, layer)

def update_layer(existing_layer, layer_update: LayerUpdate, db: Session):
    return repo.update_layer(db, existing_layer, layer_update.dict())

def delete_layer(existing_layer, db: Session):
    repo.delete_layer(db, existing_layer)

def get_digital_twins_for_layer(layer_id: int, db: Session):
    return repo.get_digital_twins_for_layer(db, layer_id)

def get_layers_filtered_paginated(
    db: Session,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    sort_column: str = "title",
    sort_direction: str = "asc",
    is_background: bool | None = None
):
    return repo.get_filtered_paginated(
        db,
        search,
        page,
        page_size,
        sort_column,
        sort_direction,
        is_background
    )