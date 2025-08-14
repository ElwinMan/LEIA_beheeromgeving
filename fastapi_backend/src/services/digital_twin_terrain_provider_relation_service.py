from sqlalchemy.orm import Session
import repositories.digital_twin_tool_relation_repository as repo
import repositories.terrain_provider_repository as terrain_provider_repo
import services.content_type_service as content_type_service
import services.tool_service as tool_service
from models.associations import DigitalTwinToolAssociation
from models.tool_associations import TerrainProvider
from typing import List
from schemas.digital_twin_tool_association_schema import DigitalTwinToolBulkItem

def handle_bulk_terrain_provider_operations(digital_twin_id: int, operations: List[DigitalTwinToolBulkItem], db: Session):
    """Handle bulk terrain provider operations for digital twin - using cesium tool with polymorphic associations"""
    result_counter = {"created": 0, "updated": 0, "deleted": 0}
    
    # Get terrain provider content type
    terrain_provider_content_type = content_type_service.get_content_type_by_name(db, "terrain_provider")
    if not terrain_provider_content_type:
        raise ValueError("Terrain provider content type not found")
    
    # Get cesium tool (terrain providers are associated with cesium tool)
    cesium_tool = tool_service.get_tool_by_name("cesium", db)
    if not cesium_tool:
        raise ValueError("Cesium tool not found")

    def handle_create(op: DigitalTwinToolBulkItem):
        # Use the cesium tool ID
        actual_tool_id = cesium_tool.id
        
        # Check if association already exists
        assoc = repo.get_tool_association(
            db, digital_twin_id, actual_tool_id, terrain_provider_content_type.id, op.content_id
        )
        if assoc is None:
            # Verify the terrain provider exists
            if op.content_id:
                terrain_provider = terrain_provider_repo.get_by_id(db, op.content_id)
                if not terrain_provider:
                    raise ValueError(f"Terrain provider with id {op.content_id} not found")
            
            assoc = DigitalTwinToolAssociation(
                digital_twin_id=digital_twin_id,
                tool_id=actual_tool_id,
                content_type_id=terrain_provider_content_type.id,
                content_id=op.content_id,
                sort_order=op.sort_order or 0
            )
            repo.bulk_create_tool_association(db, assoc)
            result_counter["created"] += 1

    def handle_update(op: DigitalTwinToolBulkItem):
        # Use the cesium tool ID
        actual_tool_id = cesium_tool.id
        
        assoc = repo.get_tool_association(
            db, digital_twin_id, actual_tool_id, terrain_provider_content_type.id, op.content_id
        )
        if assoc:
            updates = {"sort_order": op.sort_order if op.sort_order is not None else assoc.sort_order}
            updates = {k: v for k, v in updates.items() if v is not None}
            repo.bulk_update_tool_association(db, assoc, updates)
            result_counter["updated"] += 1

    def handle_delete(op: DigitalTwinToolBulkItem):
        # Use the cesium tool ID
        actual_tool_id = cesium_tool.id
        
        assoc = repo.get_tool_association(
            db, digital_twin_id, actual_tool_id, terrain_provider_content_type.id, op.content_id
        )
        if assoc:
            repo.bulk_delete_tool_association(db, assoc)
            result_counter["deleted"] += 1

    dispatch = {
        "create": handle_create,
        "update": handle_update,
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

def get_digital_twin_terrain_providers(digital_twin_id: int, db: Session):
    """Get terrain providers associated with cesium tool for this digital twin"""
    terrain_provider_content_type = content_type_service.get_content_type_by_name(db, "terrain_provider")
    if not terrain_provider_content_type:
        return []
    
    # Get cesium tool
    cesium_tool = tool_service.get_tool_by_name("cesium", db)
    if not cesium_tool:
        return []
    
    associations = repo.get_associations_by_digital_twin(db, digital_twin_id)
    terrain_provider_associations = [
        assoc for assoc in associations 
        if (assoc.tool_id == cesium_tool.id and 
            assoc.content_type_id == terrain_provider_content_type.id and 
            assoc.content_id)
    ]
    
    return sorted(terrain_provider_associations, key=lambda x: x.sort_order)
