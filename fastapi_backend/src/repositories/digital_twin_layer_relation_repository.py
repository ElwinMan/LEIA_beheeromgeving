from sqlalchemy.orm import Session
from models.digital_twin import DigitalTwinLayerAssociation
from typing import Optional

def get_layer_association(db: Session, digital_twin_id: int, layer_id: int) -> Optional[DigitalTwinLayerAssociation]:
    return (
        db.query(DigitalTwinLayerAssociation)
        .filter_by(digital_twin_id=digital_twin_id, layer_id=layer_id)
        .first()
    )

def add_layer_association(db: Session, association: DigitalTwinLayerAssociation):
    db.add(association)
    db.commit()
    db.refresh(association)
    return association

def update_layer_association(db: Session, assoc: DigitalTwinLayerAssociation):
    db.commit()
    db.refresh(assoc)
    return assoc

def delete_layer_association(db: Session, association: DigitalTwinLayerAssociation):
    db.delete(association)
    db.commit()

# Query for bulk edits without commiting till all operations are successful
def bulk_create_layer_association(db: Session, association: DigitalTwinLayerAssociation):
    db.add(association)

def bulk_update_layer_fields(assoc: DigitalTwinLayerAssociation, updates: dict):
    for field, value in updates.items():
        if value is not None:
            setattr(assoc, field, value)

def bulk_delete_layer_association(db: Session, assoc: DigitalTwinLayerAssociation):
    db.delete(assoc)