from sqlalchemy.orm import Session
import repositories.cesium_repository as repo
from models.tool_associations import TerrainProvidersSnippets
from schemas.cesium_schema import (
    CesiumSnippetCreate,
    CesiumSnippetUpdate,
)

def get_snippet(db: Session, snippet_id: int) -> TerrainProvidersSnippets | None:
    return repo.get_by_id(db, snippet_id)

def get_all_snippets(db: Session) -> list[TerrainProvidersSnippets]:
    return repo.get_all(db)

def create_snippet(db: Session, data: CesiumSnippetCreate) -> TerrainProvidersSnippets:
    snippet = TerrainProvidersSnippets(**data.dict())
    return repo.create(db, snippet)

def update_snippet(db: Session, snippet_id: int, updates: CesiumSnippetUpdate) -> TerrainProvidersSnippets | None:
    snippet = repo.get_by_id(db, snippet_id)
    if not snippet:
        return None
    return repo.update(db, snippet, updates.dict(exclude_unset=True))

def delete_snippet(db: Session, snippet_id: int) -> bool:
    return repo.delete(db, snippet_id)