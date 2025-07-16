from sqlalchemy.orm import Session
from schemas.group_schema import GroupCreate, GroupUpdate
import repositories.group_repository as repo
from models.group import Group

def get_group(group_id: int, db: Session) -> Group | None:
    return repo.get_group_by_id(db, group_id)

def list_groups(digital_twin_id: int, db: Session) -> list[Group]:
    return repo.get_groups_by_digital_twin_id(db, digital_twin_id)

def create_group(digital_twin_id: int, group_create: GroupCreate, db: Session) -> Group:
    data = group_create.dict()
    data["digital_twin_id"] = digital_twin_id
    return repo.insert_group(db, data)

def update_group(digital_twin_id: int, group_id: int, group_update: GroupUpdate, db: Session) -> Group | None:
    group = repo.get_group_by_id(db, group_id)
    if not group or group.digital_twin_id != digital_twin_id:
        return None
    return repo.update_group(db, group, group_update.dict(exclude_unset=True))

def delete_group(digital_twin_id: int, group_id: int, db: Session) -> bool:
    group = repo.get_group_by_id(db, group_id)
    if not group or group.digital_twin_id != digital_twin_id:
        return False
    repo.delete_group(db, group)
    return True