from sqlalchemy.orm import Session
import repositories.project_repository as repository
from models.tool_associations import Project
from schemas.project_schema import (
    ProjectCreate,
    ProjectUpdate,
)

def get_project(db: Session, project_id: int) -> Project | None:
    return repository.get_by_id(db, project_id)

def get_all_projects(db: Session) -> list[Project]:
    return repository.get_all(db)

def create_project(db: Session, data: ProjectCreate) -> Project:
    project = Project(**data.dict())
    return repository.create(db, project)

def update_project(db: Session, project_id: int, updates: ProjectUpdate) -> Project | None:
    project = repository.get_by_id(db, project_id)
    if not project:
        return None
    return repository.update(db, project, updates.dict(exclude_unset=True))

def delete_project(db: Session, project_id: int) -> bool:
    return repository.delete(db, project_id)

def get_projects_filtered_paginated(
    db: Session,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    sort_column: str = "name",
    sort_direction: str = "asc"
):
    return repository.get_filtered_paginated(
        db,
        search,
        page,
        page_size,
        sort_column,
        sort_direction
    )