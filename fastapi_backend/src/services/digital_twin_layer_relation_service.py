from sqlalchemy.orm import Session
import repositories.digital_twin_layer_relation_repository as repo
from models.associations import DigitalTwinLayerAssociation
from schemas.digital_twin_layer_association_schema import DigitalTwinLayerAssociationCreate, DigitalTwinLayerRelationUpdate, DigitalTwinLayerBulkItem
from typing import List

def add_layer_association(digital_twin_id: int, layer_data: DigitalTwinLayerAssociationCreate, db: Session):
    association = DigitalTwinLayerAssociation(
        digital_twin_id=digital_twin_id,
        layer_id=layer_data.layer_id,
        group_id=layer_data.group_id,
        sort_order=layer_data.sort_order,
        is_default=layer_data.is_default
    )
    return repo.add_layer_association(db, association)

def update_layer_relation(digital_twin_id: int, layer_id: int, update_data: DigitalTwinLayerRelationUpdate, db: Session):
    assoc = repo.get_layer_association(db, digital_twin_id, layer_id)
    if not assoc:
        return None

    if update_data.is_default is not None:
        assoc.is_default = update_data.is_default
    if update_data.sort_order is not None:
        assoc.sort_order = update_data.sort_order
    if update_data.group_id is not None:
        assoc.group_id = update_data.group_id

    return repo.update_layer_association(db, assoc)

def delete_layer_relation(digital_twin_id: int, layer_id: int, db: Session):
    assoc = repo.get_layer_association(db, digital_twin_id, layer_id)
    if not assoc:
        return False

    repo.delete_layer_association(db, assoc)
    return True

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