from sqlalchemy.orm import Session
from models.digital_twin import DigitalTwin

def get_digital_twin_by_id(db: Session, digital_twin_id: int):
    return db.query(DigitalTwin).filter(DigitalTwin.id == digital_twin_id).first()

def get_all_digital_twins(db: Session):
    return db.query(DigitalTwin).all()

def insert_digital_twin(db: Session, digital_twin: DigitalTwin):
    db.add(digital_twin)
    db.commit()
    db.refresh(digital_twin)
    return digital_twin

def update_digital_twin(db: Session, digital_twin: DigitalTwin, updates: dict):
    for field, value in updates.items():
        setattr(digital_twin, field, value)
    db.commit()
    db.refresh(digital_twin)
    return digital_twin

def delete_digital_twin(db: Session, digital_twin: DigitalTwin):
    db.delete(digital_twin)
    db.commit()