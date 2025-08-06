from sqlalchemy.orm import Session
import repositories.digital_twin_tool_relation_repository as repo
import repositories.bookmark_repository as bookmark_repo
import services.content_type_service as content_type_service
import services.tool_service as tool_service
from models.associations import DigitalTwinToolAssociation
from models.tool_associations import Bookmark
from typing import List
from schemas.digital_twin_tool_association_schema import DigitalTwinToolBulkItem

def handle_bulk_bookmark_operations(digital_twin_id: int, operations: List[DigitalTwinToolBulkItem], db: Session):
    """Handle bulk bookmark operations for digital twin"""
    result_counter = {"created": 0, "updated": 0, "deleted": 0}
    
    # Get bookmark content type
    bookmark_content_type = content_type_service.get_content_type_by_name(db, "bookmark")
    if not bookmark_content_type:
        raise ValueError("Bookmark content type not found")
    
    # Get bookmarks tool
    bookmarks_tool = tool_service.get_tool_by_name("bookmarks", db)
    if not bookmarks_tool:
        raise ValueError("Bookmarks tool not found")

    def handle_create(op: DigitalTwinToolBulkItem):
        # Use the actual bookmarks tool ID instead of the one from frontend
        actual_tool_id = bookmarks_tool.id
        
        # Check if association already exists
        assoc = repo.get_tool_association(
            db, digital_twin_id, actual_tool_id, bookmark_content_type.id, op.content_id
        )
        if assoc is None:
            # Verify the bookmark exists
            if op.content_id:
                bookmark = bookmark_repo.get_by_id(db, op.content_id)
                if not bookmark:
                    raise ValueError(f"Bookmark with id {op.content_id} not found")
            
            assoc = DigitalTwinToolAssociation(
                digital_twin_id=digital_twin_id,
                tool_id=actual_tool_id,
                content_type_id=bookmark_content_type.id,
                content_id=op.content_id,
                sort_order=op.sort_order or 0
            )
            repo.bulk_create_tool_association(db, assoc)
            result_counter["created"] += 1

    def handle_update(op: DigitalTwinToolBulkItem):
        # Use the actual bookmarks tool ID instead of the one from frontend
        actual_tool_id = bookmarks_tool.id
        
        assoc = repo.get_tool_association(
            db, digital_twin_id, actual_tool_id, bookmark_content_type.id, op.content_id
        )
        if assoc:
            updates = {"sort_order": op.sort_order if op.sort_order is not None else assoc.sort_order}
            updates = {k: v for k, v in updates.items() if v is not None}
            repo.bulk_update_tool_association(db, assoc, updates)
            result_counter["updated"] += 1

    def handle_delete(op: DigitalTwinToolBulkItem):
        # Use the actual bookmarks tool ID instead of the one from frontend
        actual_tool_id = bookmarks_tool.id
        
        assoc = repo.get_tool_association(
            db, digital_twin_id, actual_tool_id, bookmark_content_type.id, op.content_id
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

def get_digital_twin_bookmarks(digital_twin_id: int, db: Session):
    bookmark_content_type = content_type_service.get_content_type_by_name(db, "bookmark")
    if not bookmark_content_type:
        return []
    
    associations = repo.get_associations_by_digital_twin(db, digital_twin_id)
    bookmark_associations = [
        assoc for assoc in associations 
        if assoc.content_type_id == bookmark_content_type.id and assoc.content_id
    ]
    
    return sorted(bookmark_associations, key=lambda x: x.sort_order)
