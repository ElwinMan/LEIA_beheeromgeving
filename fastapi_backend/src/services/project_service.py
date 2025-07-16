from sqlalchemy.orm import Session
import repositories.project_repository as repository
from models.tool_associations import ProjectsSnippets
from schemas.project_schema import (
    ProjectSnippetCreate,
    ProjectSnippetUpdate,
)

def get_snippet(db: Session, snippet_id: int) -> ProjectsSnippets | None:
    return repository.get_by_id(db, snippet_id)

def get_all_snippets(db: Session) -> list[ProjectsSnippets]:
    return repository.get_all(db)

def create_snippet(db: Session, data: ProjectSnippetCreate) -> ProjectsSnippets:
    snippet = ProjectsSnippets(**data.dict())
    return repository.create(db, snippet)

def update_snippet(db: Session, snippet_id: int, updates: ProjectSnippetUpdate) -> ProjectsSnippets | None:
    snippet = repository.get_by_id(db, snippet_id)
    if not snippet:
        return None
    return repository.update(db, snippet, updates.dict(exclude_unset=True))

def delete_snippet(db: Session, snippet_id: int) -> bool:
    return repository.delete(db, snippet_id)