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

def get_filtered_paginated(
    db: Session,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    sort_column: str = "name",
    sort_direction: str = "asc"
):
    query = db.query(DigitalTwin)
    if search:
        search_lower = f"%{search.lower()}%"
        query = query.filter(
            (DigitalTwin.name.ilike(search_lower)) |
            (DigitalTwin.title.ilike(search_lower)) |
            (DigitalTwin.subtitle.ilike(search_lower)) |
            (DigitalTwin.owner.ilike(search_lower))
        )
    # Sorting
    allowed_columns = ["name", "title", "subtitle", "owner", "private", "last_updated", "id"]
    if sort_column in allowed_columns:
        sort_attr = getattr(DigitalTwin, sort_column)
        if sort_direction == "desc":
            sort_attr = sort_attr.desc()
        query = query.order_by(sort_attr)
    total = query.count()
    results = query.offset((page - 1) * page_size).limit(page_size).all()
    return results, total