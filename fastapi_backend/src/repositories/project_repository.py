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