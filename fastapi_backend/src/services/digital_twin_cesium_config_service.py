from sqlalchemy.orm import Session
import repositories.digital_twin_tool_relation_repository as repo
import services.tool_service as tool_service
from models.associations import DigitalTwinToolAssociation
from typing import Dict, Any, Optional

def get_cesium_configuration(digital_twin_id: int, db: Session) -> Optional[Dict[str, Any]]:
    """Get Cesium tool configuration for a digital twin"""
    # Get cesium tool
    cesium_tool = tool_service.get_tool_by_name("cesium", db)
    if not cesium_tool:
        return None
    
    # Look for cesium tool association without content_type_id (tool-level config)
    associations = repo.get_associations_by_digital_twin(db, digital_twin_id)
    cesium_association = next(
        (assoc for assoc in associations 
         if assoc.tool_id == cesium_tool.id and 
            assoc.content_type_id is None and 
            assoc.content_id is None), 
        None
    )
    
    return cesium_association.content if cesium_association else None

def update_cesium_configuration(digital_twin_id: int, config: Dict[str, Any], db: Session):
    """Update Cesium tool configuration for a digital twin"""
    # Get cesium tool
    cesium_tool = tool_service.get_tool_by_name("cesium", db)
    if not cesium_tool:
        raise ValueError("Cesium tool not found")
    
    # Look for existing cesium tool association
    associations = repo.get_associations_by_digital_twin(db, digital_twin_id)
    cesium_association = next(
        (assoc for assoc in associations 
         if assoc.tool_id == cesium_tool.id and 
            assoc.content_type_id is None and 
            assoc.content_id is None), 
        None
    )
    
    if cesium_association:
        # Update existing configuration
        updates = {"content": config}
        repo.bulk_update_tool_association(db, cesium_association, updates)
    else:
        # Create new configuration association
        new_association = DigitalTwinToolAssociation(
            digital_twin_id=digital_twin_id,
            tool_id=cesium_tool.id,
            content_type_id=None,  # No content type for tool configuration
            content_id=None,       # No content ID for tool configuration
            sort_order=0,
            content=config
        )
        repo.bulk_create_tool_association(db, new_association)
    
    db.commit()

def delete_cesium_configuration(digital_twin_id: int, db: Session):
    """Delete Cesium tool configuration for a digital twin"""
    # Get cesium tool
    cesium_tool = tool_service.get_tool_by_name("cesium", db)
    if not cesium_tool:
        return
    
    # Look for cesium tool association
    associations = repo.get_associations_by_digital_twin(db, digital_twin_id)
    cesium_association = next(
        (assoc for assoc in associations 
         if assoc.tool_id == cesium_tool.id and 
            assoc.content_type_id is None and 
            assoc.content_id is None), 
        None
    )
    
    if cesium_association:
        repo.bulk_delete_tool_association(db, cesium_association)
        db.commit()
