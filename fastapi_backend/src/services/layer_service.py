from sqlalchemy.orm import Session
from schemas.layer_schema import LayerCreate
import repositories.layer_repository as repo

def get_layer(layer_id: int, db: Session):
    return repo.get_layer_by_id(db, layer_id)

def list_layers(db: Session):
    return repo.get_all_layers(db)

def create_layer(layer_create: LayerCreate, db: Session):
    return repo.insert_layer(db, layer_create.dict())

def update_layer(existing_layer, layer_update: LayerCreate, db: Session):
    return repo.update_layer(db, existing_layer, layer_update.dict())

def delete_layer(existing_layer, db: Session):
    repo.delete_layer(db, existing_layer)