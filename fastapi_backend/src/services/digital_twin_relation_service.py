from sqlalchemy.orm import Session
import repositories.digital_twin_relation_repository as repo
from models.associations import DigitalTwinLayerAssociation
from schemas.digital_twin_layer_association_schema import DigitalTwinLayerAssociationCreate, DigitalTwinRelationUpdate

def add_layer_association(digital_twin_id: int, layer_data: DigitalTwinLayerAssociationCreate, db: Session):
    association = DigitalTwinLayerAssociation(
        digital_twin_id=digital_twin_id,
        layer_id=layer_data.layer_id,
        group_id=layer_data.group_id,
        sort_order=layer_data.sort_order,
    )
    return repo.add_layer_association(db, association)

def update_relation(digital_twin_id: int, layer_id: int, update_data: DigitalTwinRelationUpdate, db: Session):
    assoc = repo.get_layer_association(db, digital_twin_id, layer_id)
    if not assoc:
        return None

    if update_data.sort_order is not None:
        assoc.sort_order = update_data.sort_order
    if update_data.group_id is not None:
        assoc.group_id = update_data.group_id

    return repo.update_layer_association(db, assoc)

def delete_relation(digital_twin_id: int, layer_id: int, db: Session):
    assoc = repo.get_layer_association(db, digital_twin_id, layer_id)
    if not assoc:
        return False

    repo.delete_layer_association(db, assoc)
    return True