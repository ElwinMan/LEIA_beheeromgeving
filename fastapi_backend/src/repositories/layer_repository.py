from sqlalchemy.orm import Session
from models.layer import Layer
from typing import Optional, Dict, Any

def get_layer_by_id(db: Session, layer_id: int):
    return db.query(Layer).filter(Layer.id == layer_id).first()

def get_all_layers(db: Session):
    return db.query(Layer).all()

def create_layer(
    db: Session,
    type: str,
    title: str,
    url: str,
    featureName: str,
    isBackground: bool,
    defaultOn: bool,
    content: Optional[Dict[str, Any]] = None,
):
    layer = Layer(
        type=type,
        title=title,
        url=url,
        featureName=featureName,
        isBackground=isBackground,
        defaultOn=defaultOn,
        content=content,
    )
    db.add(layer)
    db.commit()
    db.refresh(layer)
    return layer