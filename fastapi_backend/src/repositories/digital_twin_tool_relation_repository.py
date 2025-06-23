from sqlalchemy.orm import Session
from models.digital_twin import DigitalTwinToolAssociation
from typing import Optional

def get_tool_association(db: Session, digital_twin_id: int, tool_id: int) -> Optional[DigitalTwinToolAssociation]:
    return (
        db.query(DigitalTwinToolAssociation)
        .filter_by(digital_twin_id=digital_twin_id, tool_id=tool_id)
        .first()
    )

def add_tool_association(db: Session, association: DigitalTwinToolAssociation):
    db.add(association)
    db.commit()
    db.refresh(association)
    return association

def delete_tool_association(db: Session, association: DigitalTwinToolAssociation):
    db.delete(association)
    db.commit()