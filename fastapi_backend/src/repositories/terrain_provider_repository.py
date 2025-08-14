from sqlalchemy.orm import Session
from models.tool_associations import TerrainProvider

def get_by_id(db: Session, terrainProvider_id: int):
    return db.query(TerrainProvider).filter_by(id=terrainProvider_id).first()

def get_by_ids(db: Session, terrain_provider_ids: list):
    return db.query(TerrainProvider).filter(TerrainProvider.id.in_(terrain_provider_ids)).all()

def get_all(db: Session):
    return db.query(TerrainProvider).all()

def create(db: Session, terrainProvider: TerrainProvider):
    db.add(terrainProvider)
    db.commit()
    db.refresh(terrainProvider)
    return terrainProvider

def update(db: Session, terrainProvider: TerrainProvider, updates: dict):
    for key, value in updates.items():
        setattr(terrainProvider, key, value)
    db.commit()
    db.refresh(terrainProvider)
    return terrainProvider

def delete(db: Session, terrainProvider_id: int):
    terrainProvider = db.query(TerrainProvider).filter_by(id=terrainProvider_id).first()
    if terrainProvider:
        db.delete(terrainProvider)
        db.commit()
    return terrainProvider

def get_filtered_paginated(
    db: Session,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    sort_column: str = "title",
    sort_direction: str = "asc"
):
    query = db.query(TerrainProvider)
    if search:
        search_lower = f"%{search.lower()}%"
        query = query.filter(
            (TerrainProvider.title.ilike(search_lower)) |
            (TerrainProvider.url.ilike(search_lower))
        )
    allowed_columns = ["title", "url", "vertexNormals", "id"]
    if sort_column in allowed_columns:
        sort_attr = getattr(TerrainProvider, sort_column)
        if sort_direction == "desc":
            sort_attr = sort_attr.desc()
        query = query.order_by(sort_attr)
    total = query.count()
    results = query.offset((page - 1) * page_size).limit(page_size).all()
    return results, total