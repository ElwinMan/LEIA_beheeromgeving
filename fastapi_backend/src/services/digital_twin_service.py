from sqlalchemy.orm import Session
from repositories import digital_twin_repository

def get_digital_twin(digital_twin_id: int, db: Session):
    return digital_twin_repository.get_digital_twin_by_id(db, digital_twin_id)

def list_digital_twins(db: Session):
    return digital_twin_repository.get_all_digital_twins(db)

def register_digital_twin(name: str, email: str, db: Session):
    return digital_twin_repository.create_digital_twin(db, name, email)