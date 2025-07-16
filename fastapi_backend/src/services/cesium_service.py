from sqlalchemy.orm import Session
import repositories.cesium_repository as repo
from models.tool_associations import Cesium
from schemas.cesium_schema import (
    CesiumCreate,
    CesiumUpdate,
)

def get_cesium(db: Session, cesium_id: int) -> Cesium | None:
    return repo.get_by_id(db, cesium_id)

def get_all_cesiums(db: Session) -> list[Cesium]:
    return repo.get_all(db)

def create_cesium(db: Session, data: CesiumCreate) -> Cesium:
    cesium = Cesium(**data.dict())
    return repo.create(db, cesium)

def update_cesium(db: Session, cesium_id: int, updates: CesiumUpdate) -> Cesium | None:
    cesium = repo.get_by_id(db, cesium_id)
    if not cesium:
        return None
    return repo.update(db, cesium, updates.dict(exclude_unset=True))

def delete_cesium(db: Session, cesium_id: int) -> bool:
    return repo.delete(db, cesium_id)