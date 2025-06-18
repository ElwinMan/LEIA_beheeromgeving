from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from services import layer_service
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/layers", tags=["Layers"])

class layer_Create(BaseModel):
    type: str
    title: str
    beschrijving: str
    url: str
    featureName: str
    isBackground: bool
    defaultOn: bool
    content: Optional[Dict[str, Any]] = None

@router.get("/{layer_id}")
def read_layer(layer_id: int, db: Session = Depends(get_db)):
    layer_ = layer_service.get_layer(layer_id, db)
    if not layer_:
        raise HTTPException(status_code=404, detail="Layer_ not found")
    return layer_

@router.get("/")
def read_all_layer(db: Session = Depends(get_db)):
    return layer_service.list_layers(db)

@router.post("/")
def create_layer(layer: layer_Create, db: Session = Depends(get_db)):
    return layer_service.register_layer(
        layer.type,
        layer.title,
        layer.beschrijving,
        layer.url,
        layer.featureName,
        layer.isBackground,
        layer.defaultOn,
        layer.content,
        db
    )
