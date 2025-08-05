from sqlalchemy.orm import Session
import repositories.project_repository as repository
import repositories.digital_twin_tool_relation_repository as tool_relation_repo
import services.content_type_service as content_type_service
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
    # Check if the project exists first
    project = repository.get_by_id(db, project_id)
    if not project:
        return False
    
    try:
        # Get the project content type
        project_content_type = content_type_service.get_content_type_by_name(db, "project")
        
        if project_content_type:
            # Delete all digital_twin_tool_association records that reference this project
            from models.associations import DigitalTwinToolAssociation
            associations = db.query(DigitalTwinToolAssociation).filter(
                DigitalTwinToolAssociation.content_type_id == project_content_type.id,
                DigitalTwinToolAssociation.content_id == project_id
            ).all()
            
            for assoc in associations:
                db.delete(assoc)
        
        # Delete the project itself
        db.delete(project)
        db.commit()
        return True
        
    except Exception:
        db.rollback()
        raise

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