from sqlalchemy.orm import Session
from models.associations import DigitalTwinToolAssociation
from typing import Optional

def get_tool_association(db: Session, digital_twin_id: int, tool_id: int, content_type_id: int = None, content_id: int = None) -> Optional[DigitalTwinToolAssociation]:
    query = db.query(DigitalTwinToolAssociation).filter_by(
        digital_twin_id=digital_twin_id, 
        tool_id=tool_id
    )
    
    if content_type_id is not None:
        query = query.filter_by(content_type_id=content_type_id)
    if content_id is not None:
        query = query.filter_by(content_id=content_id)
    
    return query.first()

def get_associations_by_digital_twin(db: Session, digital_twin_id: int):
    return (
        db.query(DigitalTwinToolAssociation)
        .filter_by(digital_twin_id=digital_twin_id)
        .order_by(DigitalTwinToolAssociation.sort_order)
        .all()
    )

def bulk_create_tool_association(db: Session, association: DigitalTwinToolAssociation):
    db.add(association)

def bulk_update_tool_association(db: Session, association: DigitalTwinToolAssociation, updates: dict):
    for key, value in updates.items():
        setattr(association, key, value)

def bulk_delete_tool_association(db: Session, assoc: DigitalTwinToolAssociation):
    db.delete(assoc)