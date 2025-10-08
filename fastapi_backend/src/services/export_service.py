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
import copy

from schemas.layer_schema import LayerResponse
from schemas.viewer_schema import ViewerResponse
from schemas.group_schema import GroupResponse
from schemas.tool_schema import ToolResponse

from sqlalchemy.orm import Session

def transform_layer(layer, assoc=None):
    content = layer.content if isinstance(layer.content, dict) else {}
    
    # Get association content for per-digital-twin overrides
    assoc_content = assoc.content if assoc and isinstance(assoc.content, dict) else {}
    
    # Settings always include these keys if relevant for the layer type
    settings_always_include = {"url", "featureName", "contentType"}
    settings = {}
    settings["url"] = layer.url
    settings["featureName"] = layer.featureName or ""

    if layer.type == "wms":
        wms_content = content.get("wms", {})
        for k in ["contentType"]:
            settings[k] = wms_content.get(k, "")
        # Add other wms keys only if non-empty
        for k, v in wms_content.items():
            if k not in settings_always_include and v not in (None, ""):
                settings[k] = v

    elif layer.type == "wmts":
        wmts_content = content.get("wmts", {})
        for k in ["contentType"]:
            settings[k] = wmts_content.get(k, "")
        # Add other wmts keys only if non-empty
        for k, v in wmts_content.items():
            if k not in settings_always_include and v not in (None, ""):
                settings[k] = v
        # Add extra wmts keys if non-empty
        for k in ["matrixids", "tileMatrixSetID", "tileWidth", "tileHeight", "maximumLevel"]:
            v = wmts_content.get(k, None)
            if k not in settings and v not in (None, ""):
                settings[k] = v

    elif layer.type == "3DTiles":
        tiles3d = content.get("tiles3d", {})
        for k, v in tiles3d.items():
            if v not in (None, ""):
                settings[k] = v

    elif layer.type == "geojson":
        geojson_settings = content.get("geojson", {})
        for k, v in geojson_settings.items():
            if v not in (None, ""):
                settings[k] = v

    elif layer.type == "modelanimation":
        modelanimation = content.get("modelanimation", {})
        for k, v in modelanimation.items():
            if v not in (None, ""):
                settings[k] = v

    # Always include these keys, even if empty
    always_include = {"imageUrl", "legendUrl", "groupId", "isBackground", "defaultAddToManager", "defaultOn"}
    # Prepare all possible keys and their values
    # For transparent and opacity, prioritize association content over layer content
    all_keys = {
        "id": str(layer.id),
        "type": layer.type,
        "title": layer.title,
        "groupId": str(assoc.group_id) if assoc and assoc.group_id is not None else "",
        "imageUrl": content.get("imageUrl", ""),
        "legendUrl": content.get("legendUrl", ""),
        "isBackground": layer.isBackground,
        "defaultAddToManager": content.get("defaultAddToManager", False),
        "defaultOn": assoc.is_default if assoc else True,
        "description": content.get("description", ""),
        "attribution": content.get("attribution", ""),
        "metadata": content.get("metadata", ""),
        "disablePopup": assoc_content.get("disablePopup", content.get("disablePopup", False)),
        "transparent": assoc_content.get("transparent", content.get("transparent", False)),
        "opacity": assoc_content.get("opacity", content.get("opacity", 100)),
        "cameraPosition": content.get("cameraPosition", "")
    }
    # Build the export dict
    layer_dict = {}
    for k, v in all_keys.items():
        if k in always_include:
            layer_dict[k] = v
        # Only export disablePopup if it's True
        elif k == "disablePopup":
            if v:
                layer_dict[k] = v
        # Only export opacity if transparent is true
        elif k == "opacity":
            if all_keys.get("transparent", False):
                layer_dict[k] = v
        # Only export transport if it's True
        elif k == "transparent":
            if v: 
                layer_dict[k] = v
        else:
            if v not in (None, ""):
                layer_dict[k] = v
    # Add settings at the end
    layer_dict["settings"] = settings
    return layer_dict


def build_viewer_export(digital_twin, viewer):
    """Build the viewer export structure with extracted fields"""
    viewer_export = {
        "title": digital_twin.title,
        "subtitle": digital_twin.subtitle,
        "isPrivate": digital_twin.isPrivate
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
            # Use chapter.title and chapter.buttonText, fallback to defaults
            title = chapter.get("title") or f"Hoofdstuk {chapter_id}"
            button_text = chapter.get("buttonText") or title
            chapter_group = {
                "id": chapter_id,
                "title": title,
                "buttonText": button_text
            }
            chapter_groups.append(chapter_group)
    return chapter_groups

def export_digital_twin(db: Session, digital_twin_id: int):
    digital_twin = digital_twin_repo.get_digital_twin_by_id(db, digital_twin_id)
    if not digital_twin:
        raise ValueError("Digital twin not found")

    # Sort layer associations by sort_order
    sorted_layer_assocs = sorted(digital_twin.layer_associations, key=lambda assoc: getattr(assoc, 'sort_order', 0))
    layer_ids = [assoc.layer_id for assoc in sorted_layer_assocs]
    print(layer_ids)
    layers = layer_repo.get_layers_by_ids(db, layer_ids)
    # Reorder layers to match layer_ids order
    layers_by_id = {str(layer.id): layer for layer in layers}
    ordered_layers = [layers_by_id[str(lid)] for lid in layer_ids if str(lid) in layers_by_id]

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
                            # Convert layer IDs to titles for export
                            layer_ids = project.content["layers"]
                            if isinstance(layer_ids, list):
                                layer_titles = []
                                for layer_id in layer_ids:
                                    # Find the layer by ID and get its title
                                    layer = next((l for l in layers if l.id == int(layer_id)), None)
                                    if layer:
                                        layer_titles.append(layer.title)
                                    else:
                                        # Fallback to ID if layer not found
                                        layer_titles.append(str(layer_id))
                                project_data["layers"] = layer_titles
                            else:
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
                        # Add base data from content if it exists
                        if "width" in story.content:
                            story_data["width"] = story.content["width"]
                        if "force2DMode" in story.content:
                            story_data["force2DMode"] = story.content["force2DMode"]
                        if "requestPolygonArea" in story.content:
                            story_data["requestPolygonArea"] = story.content["requestPolygonArea"]
                        if "baseLayerId" in story.content:
                            story_data["baseLayerId"] = str(story.content["baseLayerId"]) if story.content["baseLayerId"] is not None else ""
                        # Add chapters if they exist
                        if "chapters" in story.content:
                            chapters_copy = copy.deepcopy(story.content["chapters"])
                            chapter_groups = build_chapter_groups(chapters_copy)
                            if chapter_groups:
                                story_data["chapterGroups"] = chapter_groups
                            
                            # Process chapters to clean up layer properties and remove title/buttonText
                            for chapter in chapters_copy:
                                if "title" in chapter:
                                    del chapter["title"]
                                if "buttonText" in chapter:
                                    del chapter["buttonText"]
                                
                                # Process steps within each chapter
                                if "steps" in chapter and isinstance(chapter["steps"], list):
                                    for step in chapter["steps"]:
                                        if "layers" in step and isinstance(step["layers"], list):
                                            """
                                            Layer Property Cleaning Strategy:
                                            - Remove unused/frontend properties to minimize export size
                                            - Only export 'opacity' when transparency is actually enabled
                                            - Only export 'style' when custom styling is defined
                                            - Never export 'transparent' or 'title' fields - they're frontend-only
                                            - Only preserve 'id' as it's essential for layer identification
                                            """
                                            cleaned_layers = []
                                            for layer in step["layers"]:
                                                if isinstance(layer, dict):
                                                    cleaned_layer = {
                                                        "id": layer.get("id")
                                                    }
                                                    
                                                    # Only include opacity if transparent is true and opacity exists
                                                    # Note: transparent field itself is never exported, it's only used to determine if opacity should be included
                                                    if layer.get("transparent") and "opacity" in layer:
                                                        cleaned_layer["opacity"] = layer["opacity"]
                                                    
                                                    # Only include style if it has a meaningful value
                                                    if layer.get("style") and str(layer["style"]).strip():
                                                        cleaned_layer["style"] = layer["style"]
                                                    
                                                    cleaned_layers.append(cleaned_layer)
                                                else:
                                                    # Handle simple layer references (just IDs)
                                                    cleaned_layers.append(layer)
                                            
                                            step["layers"] = cleaned_layers
                            
                            story_data["chapters"] = chapters_copy

                    story_associations.append(story_data)
                elif not story:
                    # Log missing story for debugging
                    print(f"Warning: Story {assoc.content_id} referenced in association but not found in database")

    layer_associations_by_id = {
        assoc.layer_id: assoc for assoc in digital_twin.layer_associations
    }

    # Export layers: background layers first, then feature layers
    background_layers = [layer for layer in ordered_layers if getattr(layer, 'isBackground', False)]
    feature_layers = [layer for layer in ordered_layers if not getattr(layer, 'isBackground', False)]

    layers_response = [
        transform_layer(layer, layer_associations_by_id.get(layer.id))
        for layer in background_layers + feature_layers
    ]

    # Transform tools to include bookmarks, projects, and stories
    tools_with_content = []
    bookmark_tool_added = False
    project_tool_added = False
    story_tool_added = False
    
    for tool in tools:
        tool_data = ToolResponse.model_validate(tool).model_dump()
        
        # Get the tool association to access customized settings
        tool_association = next((assoc for assoc in all_tool_associations if assoc.tool_id == tool.id and assoc.content_type_id is None), None)
        
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
            
            # Check cesium settings mode setting
            cesium_settings_mode = cesium_config.get("cesiumSettingsMode", "default")
            
            # Always get terrain providers (regardless of mode)
            terrain_providers_data = []
            terrain_provider_associations = terrain_provider_service.get_digital_twin_terrain_providers(digital_twin_id, db)
            
            # Get terrain provider details
            if terrain_provider_associations:
                terrain_provider_ids = [assoc.content_id for assoc in terrain_provider_associations if assoc.content_id]
                if terrain_provider_ids:
                    terrain_providers = terrain_provider_repo.get_by_ids(db, terrain_provider_ids)
                    terrain_providers_by_id = {tp.id: tp for tp in terrain_providers}
                    
                    for assoc in terrain_provider_associations:
                        if assoc.content_id and assoc.content_id in terrain_providers_by_id:
                            tp = terrain_providers_by_id[assoc.content_id]
                            
                            # Special handling for "uit" terrain provider - only export title
                            if tp.title.lower() == "uit":
                                terrain_provider_data = {
                                    "title": tp.title
                                }
                            else:
                                terrain_provider_data = {
                                    "title": tp.title,
                                    "url": tp.url
                                }
                                
                                # Add vertexNormals if it exists and is not None
                                if tp.vertexNormals is not None:
                                    terrain_provider_data["vertexNormals"] = tp.vertexNormals
                            
                            terrain_providers_data.append(terrain_provider_data)
            
            # Always export cesium tool if there are terrain providers OR if custom mode with other settings
            if terrain_providers_data or cesium_settings_mode == "custom":
                # Create the cesium tool with proper structure
                cesium_tool = {
                    "id": "cesium",
                    "enabled": True,
                    "settings": {}
                }
                
                # Add terrain providers if we have any
                if terrain_providers_data:
                    cesium_tool["settings"]["terrainProviders"] = terrain_providers_data
                
                # Add other cesium configuration settings only if in custom mode
                if cesium_settings_mode == "custom" and cesium_config:
                    # Add configuration values to settings, excluding terrainProviders and cesiumSettingsMode
                    for key, value in cesium_config.items():
                        if key not in ["terrainProviders", "cesiumSettingsMode"]:  # We build terrainProviders from associations and exclude mode setting
                            cesium_tool["settings"][key] = value
                
                tools_with_content.append(cesium_tool)
        else:
            # Transform tool data to use name as id and add enabled: true
            transformed_tool = {
                "id": tool.name,
                "enabled": True
            }
            
            # Get settings from tool association first (user customized), then fall back to tool defaults
            settings = None
            if tool_association and tool_association.content:
                # User has customized settings stored in the association
                settings = tool_association.content
            elif tool_data.get("content") and isinstance(tool_data.get("content"), dict) and "settings" in tool_data["content"]:
                # Use default settings from tool definition
                settings = tool_data["content"]["settings"]
            
            if settings:
                # Clean connectors for layerlibrary tool only before export
                if tool.name == "layerlibrary" and "connectors" in settings:
                    def clean_connectors(connectors):
                        cleaned_connectors = []
                        for connector in connectors:
                            cleaned_connector = {}
                            for k, v in connector.items():
                                # Remove keys with empty string
                                if isinstance(v, str) and v == "":
                                    continue
                                # Remove arrays that are empty or only contain empty strings
                                elif isinstance(v, list):
                                    filtered = [item for item in v if item != ""]
                                    if filtered:
                                        cleaned_connector[k] = filtered
                                # For nested dicts (specialResources)
                                elif isinstance(v, dict):
                                    cleaned_nested = {}
                                    for nk, nv in v.items():
                                        if isinstance(nv, list):
                                            filtered_nested = [item for item in nv if item != ""]
                                            if filtered_nested:
                                                cleaned_nested[nk] = filtered_nested
                                        elif isinstance(nv, str) and nv != "":
                                            cleaned_nested[nk] = nv
                                    if cleaned_nested:
                                        cleaned_connector[k] = cleaned_nested
                                else:
                                    cleaned_connector[k] = v
                            cleaned_connectors.append(cleaned_connector)
                        return cleaned_connectors
                    settings = copy.deepcopy(settings)
                    settings["connectors"] = clean_connectors(settings["connectors"])
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


    # Export groups in parent-before-child order, recursively, and remove sort_order from output
    def export_group_hierarchy(groups, parent_id=None):
        # Get direct children of parent_id, sorted by sort_order
        children = [g for g in groups if (g.parent_id == parent_id)]
        children = sorted(children, key=lambda g: getattr(g, 'sort_order', 0))
        result = []
        for group in children:
            group_dict = GroupResponse.model_validate(group).model_dump()
            group_dict.pop('sort_order', None)
            result.append(group_dict)
            # Recursively add children
            result.extend(export_group_hierarchy(groups, group.id))
        return result

    exported_groups = export_group_hierarchy(groups, parent_id=None)

    export_data = {
        "layers": layers_response,
        "viewer": build_viewer_export(digital_twin, viewer),
        "groups": exported_groups,
        "tools": tools_with_content,
    }

    # Format filename: lowercase, spaces to underscores
    export_filename = digital_twin.name.lower().replace(' ', '_') if digital_twin.name else 'export'
    return export_filename, export_data
