from sqlalchemy.orm import Session
from models.tool_associations import Project

def get_by_id(db: Session, project_id: int):
    return db.query(Project).filter_by(id=project_id).first()

def get_all(db: Session):
    return db.query(Project).all()

def create(db: Session, project: Project):
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def update(db: Session, project: Project, updates: dict):
    for key, value in updates.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project

def delete(db: Session, project_id: int):
    project = db.query(Project).filter_by(id=project_id).first()
    if project:
        db.delete(project)
        db.commit()
    return project

def get_filtered_paginated(
    db: Session,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    sort_column: str = "name",
    sort_direction: str = "asc"
):
    query = db.query(Project)
    if search:
        search_lower = f"%{search.lower()}%"
        query = query.filter(
            (Project.name.ilike(search_lower)) |
            (Project.description.ilike(search_lower))
        )
    # Sorting
    allowed_columns = ["name", "description", "id"]
    if sort_column in allowed_columns:
        sort_attr = getattr(Project, sort_column)
        if sort_direction == "desc":
            sort_attr = sort_attr.desc()
        query = query.order_by(sort_attr)
    total = query.count()
    results = query.offset((page - 1) * page_size).limit(page_size).all()
    return results, total