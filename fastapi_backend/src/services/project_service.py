from sqlalchemy.orm import Session
import repositories.project_repository as repository
from models.tool_associations import Projects
from schemas.project_schema import (
    ProjectCreate,
    ProjectUpdate,
)

def get_project(db: Session, project_id: int) -> Projects | None:
    return repository.get_by_id(db, project_id)

def get_all_projects(db: Session) -> list[Projects]:
    return repository.get_all(db)

def create_project(db: Session, data: ProjectCreate) -> Projects:
    project = Projects(**data.dict())
    return repository.create(db, project)

def update_project(db: Session, project_id: int, updates: ProjectUpdate) -> Projects | None:
    project = repository.get_by_id(db, project_id)
    if not project:
        return None
    return repository.update(db, project, updates.dict(exclude_unset=True))

def delete_project(db: Session, project_id: int) -> bool:
    return repository.delete(db, project_id)