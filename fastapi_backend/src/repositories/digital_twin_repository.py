from sqlalchemy.orm import Session
from models.digital_twin import DigitalTwin

def get_digital_twin_by_id(db: Session, digital_twin_id: int):
    return db.query(DigitalTwin).filter(DigitalTwin.id == digital_twin_id).first()

def get_all_digital_twins(db: Session):
    return db.query(DigitalTwin).all()

def create_digital_twin(db: Session, name: str, title: str, subtitle: str, thumbnail: str):
    digital_twin = digital_twin(name=name, title=title, subtitle=subtitle, thumbnail=thumbnail)
    db.add(digital_twin)
    db.commit()
    db.refresh(digital_twin)
    return digital_twin
