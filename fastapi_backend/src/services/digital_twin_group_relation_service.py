from typing import List
from sqlalchemy.orm import Session
from schemas.group_schema import DigitalTwinGroupBulkItem
from models.group import Group
import repositories.digital_twin_group_relation_repository as repo

def handle_bulk_group_operations(digital_twin_id: int, operations: List[DigitalTwinGroupBulkItem], db: Session):
    result_counter = {"created": 0, "updated": 0, "deleted": 0}

    def handle_create(op: DigitalTwinGroupBulkItem):
        group = Group(
            digital_twin_id=digital_twin_id,
            title=op.title,
            parent_id=op.parent_id,
            sort_order=op.sort_order or 0
        )
        repo.bulk_create_group(db, group)
        result_counter["created"] += 1

    def handle_update(op: DigitalTwinGroupBulkItem):
        group = repo.get_group_by_id(db, digital_twin_id, op.id)
        if group:
            updates = {
                "title": op.title,
                "parent_id": op.parent_id,
                "sort_order": op.sort_order,
            }
            repo.bulk_update_group_fields(group, updates)
            result_counter["updated"] += 1

    def handle_delete(op: DigitalTwinGroupBulkItem):
        group = repo.get_group_by_id(db, digital_twin_id, op.id)
        if group:
            repo.bulk_delete_group(db, group)
            result_counter["deleted"] += 1

    dispatch = {
        "create": handle_create,
        "update": handle_update,
        "delete": handle_delete
    }

    try:
        for op in operations:
            handler = dispatch.get(op.action)
            if handler:
                handler(op)

        db.commit()
    except Exception:
        db.rollback()
        raise

    return result_counter
