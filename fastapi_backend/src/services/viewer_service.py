from sqlalchemy.orm import Session
from schemas.viewer_schema import ViewerCreate, ViewerUpdate
import repositories.viewer_repository as repo

def get_viewer_by_digital_twin_id(digital_twin_id: int, db: Session):
    return repo.get_viewer_by_digital_twin_id(db, digital_twin_id)

def create_viewer_with_digital_twin_id(viewer_create: ViewerCreate, digital_twin_id: int, db: Session):
    viewer_data = viewer_create.dict()
    viewer_data["digital_twin_id"] = digital_twin_id

    existing = repo.get_viewer_by_digital_twin_id(db, digital_twin_id)
    if existing:
        raise ValueError("Viewer already exists for this digital twin")

    return repo.insert_viewer(db, viewer_data)

def update_viewer_by_digital_twin_id(digital_twin_id: int, viewer_update: ViewerUpdate, db: Session):
    viewer = repo.get_viewer_by_digital_twin_id(db, digital_twin_id)
    if not viewer:
        return None
    return repo.update_viewer(db, viewer, viewer_update.dict())

def delete_viewer_by_digital_twin_id(digital_twin_id: int, db: Session):
    viewer = repo.get_viewer_by_digital_twin_id(db, digital_twin_id)
    if not viewer:
        return False
    repo.delete_viewer(db, viewer)
    return True
