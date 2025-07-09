from sqlalchemy.orm import Session
import repositories.digital_twin_layer_relation_repository as repo
from models.associations import DigitalTwinLayerAssociation
from schemas.digital_twin_layer_association_schema import DigitalTwinLayerBulkItem
from typing import List

def handle_bulk_layer_operations(digital_twin_id: int, operations: List[DigitalTwinLayerBulkItem], db: Session):
    result_counter = {"created": 0, "updated": 0, "deleted": 0}

    def handle_create(op: DigitalTwinLayerBulkItem):
        assoc = DigitalTwinLayerAssociation(
            digital_twin_id=digital_twin_id,
            layer_id=op.layer_id,
            group_id=op.group_id,
            sort_order=op.sort_order or 0,
            is_default=op.is_default or False
        )
        repo.bulk_create_layer_association(db, assoc)
        result_counter["created"] += 1

    def handle_update(op: DigitalTwinLayerBulkItem):
        assoc = repo.get_layer_association(db, digital_twin_id, op.layer_id)
        if assoc:
            updates = {
                "sort_order": op.sort_order,
                "group_id": op.group_id,
                "is_default": op.is_default,
            }
            repo.bulk_update_layer_fields(assoc, updates)
            result_counter["updated"] += 1

    def handle_delete(op: DigitalTwinLayerBulkItem):
        assoc = repo.get_layer_association(db, digital_twin_id, op.layer_id)
        if assoc:
            repo.bulk_delete_layer_association(db, assoc)
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