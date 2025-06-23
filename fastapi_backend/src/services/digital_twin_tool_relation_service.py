from sqlalchemy.orm import Session
import repositories.digital_twin_tool_relation_repository as repo
from models.associations import DigitalTwinToolAssociation
from schemas.digital_twin_tool_association_schema import DigitalTwinToolAssociationCreate

def add_tool_association(digital_twin_id: int, tool_data: DigitalTwinToolAssociationCreate, db: Session):
    association = DigitalTwinToolAssociation(
        digital_twin_id=digital_twin_id,
        tool_id=tool_data.tool_id,
    )
    return repo.add_tool_association(db, association)

def delete_relation(digital_twin_id: int, tool_id: int, db: Session):
    assoc = repo.get_tool_association(db, digital_twin_id, tool_id)
    if not assoc:
        return False

    repo.delete_tool_association(db, assoc)
    return True