import repositories.digital_twin_repository as digital_twin_repo
import repositories.layer_repository as layer_repo
import repositories.viewer_repository as viewer_repo
import repositories.group_repository as group_repo
import repositories.tool_repository as tool_repo
import repositories.digital_twin_tool_relation_repository as tool_relation_repo
import repositories.bookmark_repository as bookmark_repo
import repositories.project_repository as project_repo
import repositories.story_repository as story_repo
import repositories.terrain_provider_repository as terrain_provider_repo
import services.content_type_service as content_type_service
import services.digital_twin_cesium_config_service as cesium_config_service
import services.digital_twin_terrain_provider_relation_service as terrain_provider_service

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
        "imageUrl": layer.content.get("imageUrl", "") if layer.content and isinstance(layer.content, dict) else "",
        "legendUrl": layer.content.get("legendUrl", "") if layer.content and isinstance(layer.content, dict) else "",
        "isBackground": layer.isBackground,
        "defaultAddToManager": layer.content.get("defaultAddToManager", False) if layer.content and isinstance(layer.content, dict) else False,
        "defaultOn": assoc.is_default if assoc else True,
        "attribution": layer.content.get("attribution", "") if layer.content and isinstance(layer.content, dict) else "",
        "settings": {
            "url": layer.url,
            "featureName": layer.featureName,
            "contenttype": layer.content.get("contenttype", "") if layer.content and isinstance(layer.content, dict) else ""
        }
    }

def build_viewer_export(digital_twin, viewer):
    """Build the viewer export structure with extracted fields"""
    viewer_export = {
        "title": digital_twin.title,
        "subtitle": digital_twin.subtitle
    }
    
    if viewer and viewer.content:
        content = viewer.content
        
        # Extract specific fields to root level
        if "logo" in content:
            viewer_export["logo"] = content["logo"]
        
        if "thumbnail" in content:
            viewer_export["thumbnail"] = content["thumbnail"]
            
        if "startPosition" in content:
            viewer_export["startPosition"] = content["startPosition"]
            
        # Add remaining content fields (excluding the ones we moved to root)
        remaining_content = {
            k: v for k, v in content.items() 
            if k not in ["logo", "thumbnail", "startPosition"]
        }
        
        # Add remaining content fields to the root level
        viewer_export.update(remaining_content)
    
    return viewer_export

def build_chapter_groups(chapters):
    """Build chapterGroups from story chapters"""
    if not chapters or not isinstance(chapters, list):
        return []
    
    chapter_groups = []
    for index, chapter in enumerate(chapters):
        if isinstance(chapter, dict):
            chapter_id = str(index + 1)
            
            # Try to get title from the first step of the chapter, or use a default
            title = f"Hoofdstuk {chapter_id}"
            if "steps" in chapter and isinstance(chapter["steps"], list) and len(chapter["steps"]) > 0:
                first_step = chapter["steps"][0]
                if isinstance(first_step, dict) and "title" in first_step and first_step["title"]:
                    title = first_step["title"]
            
            # Format title with H1:, H2:, H3: etc prefix
            formatted_title = f"H{chapter_id}: {title}"
            
            chapter_group = {
                "id": chapter_id,
                "title": formatted_title,
                "buttonText": title
            }
            chapter_groups.append(chapter_group)
    
    return chapter_groups

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
    
    # Get project content type
    project_content_type = content_type_service.get_content_type_by_name(db, "project")
    project_associations = []
    
    # Get story content type
    story_content_type = content_type_service.get_content_type_by_name(db, "story")
    story_associations = []
    
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
            
            # Create bookmark entries with tool reference, but only for existing bookmarks
            for assoc in bookmark_tool_associations:
                bookmark = bookmarks_by_id.get(assoc.content_id)
                tool = next((t for t in tools if t.id == assoc.tool_id), None)
                
                # Only process if both bookmark and tool exist
                if bookmark and tool:
                    bookmark_associations.append({
                        "title": bookmark.title or "",
                        "description": bookmark.description or "",
                        "x": float(bookmark.x) if bookmark.x is not None else 0,
                        "y": float(bookmark.y) if bookmark.y is not None else 0,
                        "z": float(bookmark.z) if bookmark.z is not None else 0,
                        "heading": float(bookmark.heading) if bookmark.heading is not None else 0,
                        "pitch": float(bookmark.pitch) if bookmark.pitch is not None else 0,
                        "duration": float(bookmark.duration) if bookmark.duration is not None else 0,
                        "tool": tool.name  # Keep this for grouping
                    })
                elif not bookmark:
                    # Log missing bookmark for debugging
                    print(f"Warning: Bookmark {assoc.content_id} referenced in association but not found in database")

    if project_content_type:
        # Filter associations that are projects and have content_id
        project_tool_associations = [
            assoc for assoc in all_tool_associations 
            if assoc.content_type_id == project_content_type.id and assoc.content_id
        ]
        
        # Get project details for each association
        project_ids = [assoc.content_id for assoc in project_tool_associations]
        if project_ids:
            projects = project_repo.get_projects_by_ids(db, project_ids)
            projects_by_id = {project.id: project for project in projects}
            
            # Create project entries with tool reference and default flag, but only for existing projects
            for assoc in project_tool_associations:
                project = projects_by_id.get(assoc.content_id)
                tool = next((t for t in tools if t.id == assoc.tool_id), None)
                
                # Only process if both project and tool exist
                if project and tool:
                    project_data = {
                        "name": project.name or "",
                        "description": project.description or "",
                        "tool": tool.name,  # Keep this for grouping
                        "is_default": assoc.is_default or False  # Track default project
                    }
                    
                    # Add content fields to project data (safely handle None content)
                    if project.content and isinstance(project.content, dict):
                        if "polygon" in project.content:
                            project_data["polygon"] = project.content["polygon"]
                        if "layers" in project.content:
                            project_data["layers"] = project.content["layers"]
                        if "cameraPosition" in project.content:
                            project_data["cameraPosition"] = project.content["cameraPosition"]
                    
                    project_associations.append(project_data)
                elif not project:
                    # Log missing project for debugging
                    print(f"Warning: Project {assoc.content_id} referenced in association but not found in database")

    if story_content_type:
        # Filter associations that are stories and have content_id
        story_tool_associations = [
            assoc for assoc in all_tool_associations 
            if assoc.content_type_id == story_content_type.id and assoc.content_id
        ]
        
        # Get story details for each association
        story_ids = [assoc.content_id for assoc in story_tool_associations]
        if story_ids:
            stories = story_repo.get_stories_by_ids(db, story_ids)
            stories_by_id = {story.id: story for story in stories}
            
            # Create story entries with tool reference, but only for existing stories
            for assoc in story_tool_associations:
                story = stories_by_id.get(assoc.content_id)
                tool = next((t for t in tools if t.id == assoc.tool_id), None)
                
                # Only process if both story and tool exist
                if story and tool:
                    story_data = {
                        "name": story.name or "",
                        "description": story.description or "",
                        "tool": tool.name  # Keep this for grouping
                    }
                    
                    # Add content fields to story data (safely handle None content)
                    if story.content and isinstance(story.content, dict):
                        # Add width if it exists
                        if "width" in story.content:
                            story_data["width"] = story.content["width"]
                        # Add chapters if they exist
                        if "chapters" in story.content:
                            story_data["chapters"] = story.content["chapters"]
                            # Build chapterGroups from chapters
                            chapter_groups = build_chapter_groups(story.content["chapters"])
                            if chapter_groups:
                                story_data["chapterGroups"] = chapter_groups
                    
                    story_associations.append(story_data)
                elif not story:
                    # Log missing story for debugging
                    print(f"Warning: Story {assoc.content_id} referenced in association but not found in database")

    layer_associations_by_id = {
        assoc.layer_id: assoc for assoc in digital_twin.layer_associations
    }

    layers_response = [
        transform_layer(layer, layer_associations_by_id.get(layer.id))
        for layer in layers
    ]

    # Transform tools to include bookmarks, projects, and stories
    tools_with_content = []
    bookmark_tool_added = False
    project_tool_added = False
    story_tool_added = False
    
    for tool in tools:
        tool_data = ToolResponse.model_validate(tool).model_dump()
        
        # Get bookmarks for this specific tool and remove the tool reference
        tool_bookmarks = []
        for bookmark in bookmark_associations:
            if bookmark.get("tool") == tool.name:
                # Create a copy without the tool reference
                clean_bookmark = {k: v for k, v in bookmark.items() if k != "tool"}
                tool_bookmarks.append(clean_bookmark)
        
        # Get stories for this specific tool and remove the tool reference
        tool_stories = []
        for story in story_associations:
            if story.get("tool") == tool.name:
                # Create a copy without the tool reference
                clean_story = {k: v for k, v in story.items() if k != "tool"}
                tool_stories.append(clean_story)

        # Get projects for this specific tool and remove the tool reference
        tool_projects = []
        default_project = None
        for project in project_associations:
            if project.get("tool") == tool.name:
                # Create a copy without the tool reference and is_default flag
                clean_project = {k: v for k, v in project.items() if k not in ["tool", "is_default"]}
                tool_projects.append(clean_project)
                
                # Track the default project name
                if project.get("is_default"):
                    default_project = project.get("name")
        
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
            tools_with_content.append(bookmarks_tool)
            bookmark_tool_added = True
        # Check if this is a projects tool and there are projects
        elif tool.name == "projects" and tool_projects:
            # Create the projects tool with the proper structure
            projects_tool = {
                "id": "projects",
                "enabled": True,
                "settings": {}
            }
            
            # Add openProject first if there's a default project
            if default_project:
                projects_tool["settings"]["openProject"] = default_project
            
            # Then add the projects array
            projects_tool["settings"]["projects"] = tool_projects
            
            tools_with_content.append(projects_tool)
            project_tool_added = True
        # Check if this is a stories tool and there are stories
        elif tool.name == "stories" and tool_stories:
            # Create the stories tool with the proper structure
            stories_tool = {
                "id": "stories",
                "enabled": True,
                "settings": {
                    "stories": tool_stories
                }
            }
            tools_with_content.append(stories_tool)
            story_tool_added = True
        # Check if this is a cesium tool
        elif tool.name == "cesium":
            # Get cesium configuration
            cesium_config = cesium_config_service.get_cesium_configuration(digital_twin_id, db) or {}
            
            # Get terrain providers associated with cesium tool
            terrain_provider_associations = terrain_provider_service.get_digital_twin_terrain_providers(digital_twin_id, db)
            
            # Get terrain provider details
            terrain_providers_data = []
            if terrain_provider_associations:
                terrain_provider_ids = [assoc.content_id for assoc in terrain_provider_associations if assoc.content_id]
                if terrain_provider_ids:
                    terrain_providers = terrain_provider_repo.get_by_ids(db, terrain_provider_ids)
                    terrain_providers_by_id = {tp.id: tp for tp in terrain_providers}
                    
                    for assoc in terrain_provider_associations:
                        if assoc.content_id and assoc.content_id in terrain_providers_by_id:
                            tp = terrain_providers_by_id[assoc.content_id]
                            terrain_provider_data = {
                                "title": tp.title,
                                "url": tp.url
                            }
                            
                            # Add vertexNormals if it exists and is not None
                            if tp.vertexNormals is not None:
                                terrain_provider_data["vertexNormals"] = tp.vertexNormals
                            
                            terrain_providers_data.append(terrain_provider_data)
            
            # Create the cesium tool with proper structure
            cesium_tool = {
                "id": "cesium",
                "enabled": True,
                "settings": {}
            }
            
            # Add cesium configuration settings
            if cesium_config:
                # Add configuration values to settings, excluding terrainProviders which we handle separately
                for key, value in cesium_config.items():
                    if key != "terrainProviders":  # We build this from associations
                        cesium_tool["settings"][key] = value
            
            # Add terrain providers
            if terrain_providers_data:
                cesium_tool["settings"]["terrainProviders"] = terrain_providers_data
            
            tools_with_content.append(cesium_tool)
        else:
            # Transform tool data to use name as id and add enabled: true
            transformed_tool = {
                "id": tool.name,
                "enabled": True
            }
            
            # Add settings from either direct settings or content.settings
            settings = tool_data.get("content", {}).get("settings") if tool_data.get("content") and isinstance(tool_data.get("content"), dict) else None
            
            if settings:
                transformed_tool["settings"] = settings
            
            # For other tools, add bookmarks to existing settings if there are any
            if tool_bookmarks and tool.name != "bookmarks":
                if "settings" not in transformed_tool:
                    transformed_tool["settings"] = {}
                transformed_tool["settings"]["bookmarks"] = tool_bookmarks
            
            # For other tools, add projects to existing settings if there are any
            # BUT exclude layerlibrary tool from getting projects
            if tool_projects and tool.name != "projects" and tool.name != "layerlibrary":
                if "settings" not in transformed_tool:
                    transformed_tool["settings"] = {}
                transformed_tool["settings"]["projects"] = tool_projects
                
                # Add openProject if there's a default project
                if default_project:
                    transformed_tool["settings"]["openProject"] = default_project
            
            tools_with_content.append(transformed_tool)
    
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
            tools_with_content.append(bookmarks_tool)

    # If we have project associations but no projects tool was found, create one
    if project_associations and not project_tool_added:
        # Collect all projects that weren't assigned to any specific tool
        unassigned_projects = []
        default_project = None
        for project in project_associations:
            # Remove the tool reference and is_default flag for the final output
            clean_project = {k: v for k, v in project.items() if k not in ["tool", "is_default"]}
            unassigned_projects.append(clean_project)
            
            # Track the default project name
            if project.get("is_default"):
                default_project = project.get("name")
        
        if unassigned_projects:
            projects_tool = {
                "id": "projects", 
                "enabled": True,
                "settings": {}
            }
            
            # Add openProject first if there's a default project
            if default_project:
                projects_tool["settings"]["openProject"] = default_project
            
            # Then add the projects array
            projects_tool["settings"]["projects"] = unassigned_projects
            
            tools_with_content.append(projects_tool)

    # If we have story associations but no stories tool was found, create one
    if story_associations and not story_tool_added:
        # Collect all stories that weren't assigned to any specific tool
        unassigned_stories = []
        for story in story_associations:
            # Remove the tool reference for the final output
            clean_story = {k: v for k, v in story.items() if k != "tool"}
            unassigned_stories.append(clean_story)
        
        if unassigned_stories:
            stories_tool = {
                "id": "stories", 
                "enabled": True,
                "settings": {
                    "stories": unassigned_stories
                }
            }
            tools_with_content.append(stories_tool)

    export_data = {
        "layers": layers_response,
        "viewer": build_viewer_export(digital_twin, viewer),
        "groups": [GroupResponse.model_validate(group).model_dump() for group in groups],
        "tools": tools_with_content,
    }

    return digital_twin.name, export_data
