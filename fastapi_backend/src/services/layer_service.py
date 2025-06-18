from sqlalchemy.orm import Session
from repositories import layer_repository
from typing import Optional, Dict, Any

def get_layer(layer_id: int, db: Session):
    return layer_repository.get_layer_by_id(db, layer_id)

def list_layers(db: Session):
    return layer_repository.get_all_layers(db)

def register_layer(
    db: Session,
    type: str,
    title: str,
    url: str,
    featureName: str,
    is_background: bool,
    defaultAddToManager: bool,
    defaultOn: bool,
    settings: Optional[Dict[str, Any]] = None,
):  return layer_repository.create_layer(
        db,
        type,
        title,
        url,
        featureName,
        is_background,
        defaultAddToManager,
        defaultOn,
        settings
    )