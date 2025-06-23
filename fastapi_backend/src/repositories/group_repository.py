from sqlalchemy.orm import Session
from models.group import Group

def get_group(db: Session, group_id: int) -> Group | None:
    return db.query(Group).filter(Group.id == group_id).first()

def get_groups_by_digital_twin(db: Session, digital_twin_id: int):
    return (
        db.query(Group)
        .filter(Group.digital_twin_id == digital_twin_id)
        .order_by(Group.sort_order)
        .all()
    )

def insert_group(db: Session, group_data: dict) -> Group:
    group = Group(**group_data)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group

def update_group(db: Session, group: Group, updates: dict) -> Group:
    for key, value in updates.items():
        setattr(group, key, value)
    db.commit()
    db.refresh(group)
    return group

def delete_group(db: Session, group: Group):
    db.delete(group)
    db.commit()