from sqlalchemy.orm import Session
import repositories.terrain_provider_repository as repo
from models.tool_associations import TerrainProvider
from schemas.terrain_provider_schema import (
    TerrainProviderCreate,
    TerrainProviderUpdate,
)

def get_terrain_provider(db: Session, terrain_provider_id: int) -> TerrainProvider | None:
    return repo.get_by_id(db, terrain_provider_id)

def get_all_terrain_providers(db: Session) -> list[TerrainProvider]:
    return repo.get_all(db)

def create_terrain_provider(db: Session, data: TerrainProviderCreate) -> TerrainProvider:
    terrain_provider = TerrainProvider(**data.dict())
    return repo.create(db, terrain_provider)

def update_terrain_provider(db: Session, terrain_provider_id: int, updates: TerrainProviderUpdate) -> TerrainProvider | None:
    terrain_provider = repo.get_by_id(db, terrain_provider_id)
    if not terrain_provider:
        return None
    return repo.update(db, terrain_provider, updates.dict(exclude_unset=True))

def delete_terrain_provider(db: Session, terrain_provider_id: int) -> bool:
    return repo.delete(db, terrain_provider_id)

def get_terrain_providers_filtered_paginated(
    db: Session,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    sort_column: str = "title",
    sort_direction: str = "asc"
):
    return repo.get_filtered_paginated(
        db,
        search,
        page,
        page_size,
        sort_column,
        sort_direction
    )