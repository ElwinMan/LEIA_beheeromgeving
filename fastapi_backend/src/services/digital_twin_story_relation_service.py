from sqlalchemy.orm import Session
from models.associations import DigitalTwinToolAssociation
from models.tool_associations import Story
from typing import List
from schemas.digital_twin_tool_association_schema import DigitalTwinToolBulkItem
import repositories.digital_twin_tool_relation_repository as repo
import repositories.story_repository as story_repo
import services.content_type_service as content_type_service
import services.tool_service as tool_service

def handle_bulk_story_operations(digital_twin_id: int, operations: List[DigitalTwinToolBulkItem], db: Session):
    """Handle bulk story operations for digital twin"""
    result_counter = {"created": 0, "updated": 0, "deleted": 0}
    
    # Get story content type
    story_content_type = content_type_service.get_content_type_by_name(db, "story")
    if not story_content_type:
        raise ValueError("Story content type not found")
    
    # Get stories tool
    stories_tool = tool_service.get_tool_by_name("stories", db)
    if not stories_tool:
        raise ValueError("Stories tool not found")

    def handle_create(op: DigitalTwinToolBulkItem):
        # Use the actual stories tool ID instead of the one from frontend
        actual_tool_id = stories_tool.id
        
        # Check if association already exists
        existing_assoc = repo.get_tool_association(
            db, digital_twin_id, actual_tool_id, story_content_type.id, op.content_id
        )
        if existing_assoc is None:
            # Verify the story exists
            if op.content_id:
                story = story_repo.get_by_id(db, op.content_id)
                if not story:
                    raise ValueError(f"Story with id {op.content_id} not found")
            
            assoc = DigitalTwinToolAssociation(
                digital_twin_id=digital_twin_id,
                tool_id=actual_tool_id,
                content_type_id=story_content_type.id,
                content_id=op.content_id,
                sort_order=op.sort_order or 0,
                is_default=op.is_default or False
            )
            repo.bulk_create_tool_association(db, assoc)
            result_counter["created"] += 1

    def handle_update(op: DigitalTwinToolBulkItem):
        # Use the actual stories tool ID instead of the one from frontend
        actual_tool_id = stories_tool.id
        
        assoc = repo.get_tool_association(
            db, digital_twin_id, actual_tool_id, story_content_type.id, op.content_id
        )
        if assoc:
            updates = {
                "sort_order": op.sort_order,
                "is_default": op.is_default or False
            }
            repo.bulk_update_tool_association(db, assoc, updates)
            result_counter["updated"] += 1

    def handle_delete(op: DigitalTwinToolBulkItem):
        # Use the actual stories tool ID instead of the one from frontend
        actual_tool_id = stories_tool.id
        
        assoc = repo.get_tool_association(
            db, digital_twin_id, actual_tool_id, story_content_type.id, op.content_id
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
            if op.action in dispatch:
                dispatch[op.action](op)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return result_counter

def get_digital_twin_stories(digital_twin_id: int, db: Session):
    """Get all stories associated with a digital twin"""
    story_content_type = content_type_service.get_content_type_by_name(db, "story")
    if not story_content_type:
        return []
    
    associations = repo.get_associations_by_digital_twin(db, digital_twin_id)
    story_associations = [
        assoc for assoc in associations 
        if assoc.content_type_id == story_content_type.id and assoc.content_id
    ]
    
    return sorted(story_associations, key=lambda x: x.sort_order)
