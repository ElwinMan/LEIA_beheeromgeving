from sqlalchemy.orm import Session
from schemas.digital_twin_schema import DigitalTwinCreate, DigitalTwinUpdate
from models.digital_twin import DigitalTwin
import repositories.digital_twin_repository as repo

def get_digital_twin(digital_twin_id: int, db: Session):
    return repo.get_digital_twin_by_id(db, digital_twin_id)

def list_digital_twins(db: Session):
    return repo.get_all_digital_twins(db)

def create_digital_twin(digital_twin_create: DigitalTwinCreate, db: Session):
    digital_twin = DigitalTwin(**digital_twin_create.dict())
    return repo.insert_digital_twin(db, digital_twin)

def update_digital_twin(existing_digital_twin: DigitalTwin, data: DigitalTwinUpdate, db: Session):
    updates = data.dict(exclude_unset=True)
    return repo.update_digital_twin(db, existing_digital_twin, updates)

def delete_digital_twin(existing_digital_twin: DigitalTwin, db: Session):
    repo.delete_digital_twin(db, existing_digital_twin)

def get_digital_twins_filtered_paginated(
    db: Session,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    sort_column: str = "name",
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