from sqlalchemy.orm import Session
from models.tool_associations import Projects

def get_by_id(db: Session, project_id: int):
    return db.query(Projects).filter_by(id=project_id).first()

def get_all(db: Session):
    return db.query(Projects).all()

def create(db: Session, project: Projects):
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def update(db: Session, project: Projects, updates: dict):
    for key, value in updates.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project

def delete(db: Session, project_id: int):
    project = db.query(Projects).filter_by(id=project_id).first()
    if project:
        db.delete(project)
        db.commit()
    return project