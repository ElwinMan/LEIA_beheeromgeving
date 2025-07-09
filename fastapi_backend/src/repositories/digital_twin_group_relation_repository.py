from sqlalchemy.orm import Session
from models.group import Group

def get_group_by_id(db: Session, digital_twin_id: int, group_id: int) -> Group:
    return db.query(Group).filter_by(id=group_id, digital_twin_id=digital_twin_id).first()

def bulk_create_group(db: Session, group: Group):
    db.add(group)

def bulk_update_group_fields(group: Group, updates: dict):
    for field, value in updates.items():
        setattr(group, field, value)

def bulk_delete_group(db: Session, group: Group):
    db.delete(group)
