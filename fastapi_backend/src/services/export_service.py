import repositories.digital_twin_repository as digital_twin_repo
import repositories.layer_repository as layer_repo
import repositories.viewer_repository as viewer_repo
import repositories.group_repository as group_repo
import repositories.tool_repository as tool_repo
import repositories.digital_twin_tool_relation_repository as tool_relation_repo
import repositories.bookmark_repository as bookmark_repo
import services.content_type_service as content_type_service

from schemas.layer_schema import LayerResponse
from schemas.viewer_schema import ViewerResponse
from schemas.group_schema import GroupResponse
from schemas.tool_schema import ToolResponse

from sqlalchemy.orm import Session

def transform_layer(layer, assoc=None):
    return {
        "id": layer.id,
        "type": layer.type,
        "title": layer.title,
        "groupId": assoc.group_id if assoc else "",
        "imageUrl": layer.content.get("imageUrl", "") if layer.content else "",
        "legendUrl": layer.content.get("legendUrl", "") if layer.content else "",
        "isBackground": layer.isBackground,
        "defaultAddToManager": layer.content.get("defaultAddToManager", False) if layer.content else False,
        "defaultOn": assoc.is_default if assoc else True,
        "attribution": layer.content.get("attribution", "") if layer.content else "",
        "settings": {
            "url": layer.url,
            "featureName": layer.featureName,
            "contenttype": layer.content.get("contenttype", "") if layer.content else ""
        }
    }

def export_digital_twin(db: Session, digital_twin_id: int):
    digital_twin = digital_twin_repo.get_digital_twin_by_id(db, digital_twin_id)
    if not digital_twin:
        raise ValueError("Digital twin not found")

    layer_ids = [assoc.layer_id for assoc in digital_twin.layer_associations]
    layers = layer_repo.get_layers_by_ids(db, layer_ids)

    viewer = viewer_repo.get_viewer_by_digital_twin_id(db, digital_twin_id)

    group_ids = list(set(assoc.group_id for assoc in digital_twin.layer_associations if assoc.group_id))
    groups = group_repo.get_groups_by_ids(db, group_ids) if group_ids else []

    tool_ids = [assoc.tool_id for assoc in digital_twin.tool_associations]
    tools = tool_repo.get_tools_by_ids(db, tool_ids)

    # Get all tool associations for this digital twin
    all_tool_associations = tool_relation_repo.get_associations_by_digital_twin(db, digital_twin_id)
    
    # Get bookmark content type
    bookmark_content_type = content_type_service.get_content_type_by_name(db, "bookmark")
    bookmark_associations = []
    
    if bookmark_content_type:
        # Filter associations that are bookmarks and have content_id
        bookmark_tool_associations = [
            assoc for assoc in all_tool_associations 
            if assoc.content_type_id == bookmark_content_type.id and assoc.content_id
        ]
        
        # Get bookmark details for each association
        bookmark_ids = [assoc.content_id for assoc in bookmark_tool_associations]
        if bookmark_ids:
            bookmarks = bookmark_repo.get_bookmarks_by_ids(db, bookmark_ids)
            bookmarks_by_id = {bookmark.id: bookmark for bookmark in bookmarks}
            
            # Create bookmark entries with tool reference
            for assoc in bookmark_tool_associations:
                bookmark = bookmarks_by_id.get(assoc.content_id)
                tool = next((t for t in tools if t.id == assoc.tool_id), None)
                
                if bookmark and tool:
                    bookmark_associations.append({
                        "title": bookmark.title or "",
                        "description": bookmark.description or "",
                        "x": bookmark.x or 0,
                        "y": bookmark.y or 0,
                        "z": bookmark.z or 0,
                        "heading": bookmark.heading or 0,
                        "pitch": bookmark.pitch or 0,
                        "duration": bookmark.duration or 0,
                        "tool": tool.name  # Keep this for grouping
                    })

    layer_associations_by_id = {
        assoc.layer_id: assoc for assoc in digital_twin.layer_associations
    }

    layers_response = [
        transform_layer(layer, layer_associations_by_id.get(layer.id))
        for layer in layers
    ]

    # Transform tools to include bookmarks
    tools_with_bookmarks = []
    bookmark_tool_added = False
    
    for tool in tools:
        tool_data = ToolResponse.model_validate(tool).model_dump()
        
        # Get bookmarks for this specific tool and remove the tool reference
        tool_bookmarks = []
        for bookmark in bookmark_associations:
            if bookmark.get("tool") == tool.name:
                # Create a copy without the tool reference
                clean_bookmark = {k: v for k, v in bookmark.items() if k != "tool"}
                tool_bookmarks.append(clean_bookmark)
        
        # Check if this is a bookmarks tool and there are bookmarks
        if tool.name == "bookmarks" and tool_bookmarks:
            # Create the bookmarks tool with the proper structure
            bookmarks_tool = {
                "id": "bookmarks",
                "enabled": True,
                "settings": {
                    "bookmarks": tool_bookmarks
                }
            }
            tools_with_bookmarks.append(bookmarks_tool)
            bookmark_tool_added = True
        else:
            # Transform tool data to use name as id and add enabled: true
            transformed_tool = {
                "id": tool.name,
                "enabled": True
            }
            
            # Add settings from either direct settings or content.settings
            settings = tool_data.get("content", {}).get("settings")
            
            if settings:
                transformed_tool["settings"] = settings
            
            # For other tools, add bookmarks to existing settings if there are any
            if tool_bookmarks and tool.name != "bookmarks":
                if "settings" not in transformed_tool:
                    transformed_tool["settings"] = {}
                transformed_tool["settings"]["bookmarks"] = tool_bookmarks
            
            tools_with_bookmarks.append(transformed_tool)
    
    # If we have bookmark associations but no bookmarks tool was found, create one
    if bookmark_associations and not bookmark_tool_added:
        # Collect all bookmarks that weren't assigned to any specific tool
        unassigned_bookmarks = []
        for bookmark in bookmark_associations:
            # Remove the tool reference for the final output
            clean_bookmark = {k: v for k, v in bookmark.items() if k != "tool"}
            unassigned_bookmarks.append(clean_bookmark)
        
        if unassigned_bookmarks:
            bookmarks_tool = {
                "id": "bookmarks", 
                "enabled": True,
                "settings": {
                    "bookmarks": unassigned_bookmarks
                }
            }
            tools_with_bookmarks.append(bookmarks_tool)

    export_data = {
        "layers": layers_response,
        "viewer": {
            "title": digital_twin.title,
            "subtitle": digital_twin.subtitle,
            **ViewerResponse.model_validate(viewer).model_dump()
        },
        "groups": [GroupResponse.model_validate(group).model_dump() for group in groups],
        "tools": tools_with_bookmarks,
    }

    return digital_twin.name, export_data
