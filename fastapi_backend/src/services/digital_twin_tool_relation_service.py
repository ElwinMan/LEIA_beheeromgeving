from sqlalchemy.orm import Session
import repositories.digital_twin_tool_relation_repository as repo
from models.associations import DigitalTwinToolAssociation
from typing import List
from schemas.digital_twin_tool_association_schema import DigitalTwinToolBulkItem

def handle_bulk_tool_operations(digital_twin_id: int, operations: List[DigitalTwinToolBulkItem], db: Session):
    result_counter = {"created": 0, "deleted": 0}

    def handle_create(op: DigitalTwinToolBulkItem):
        assoc = repo.get_tool_association(db, digital_twin_id, op.tool_id)
        if assoc is None:
            assoc = DigitalTwinToolAssociation(
                digital_twin_id=digital_twin_id,
                tool_id=op.tool_id
            )
            repo.bulk_create_tool_association(db, assoc)
            result_counter["created"] += 1

    def handle_delete(op: DigitalTwinToolBulkItem):
        assoc = repo.get_tool_association(db, digital_twin_id, op.tool_id)
        if assoc:
            repo.bulk_delete_tool_association(db, assoc)
            result_counter["deleted"] += 1

    dispatch = {
        "create": handle_create,
        "delete": handle_delete,
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