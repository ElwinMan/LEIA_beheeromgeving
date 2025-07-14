import repositories.digital_twin_repository as digital_twin_repo
import repositories.layer_repository as layer_repo
import repositories.viewer_repository as viewer_repo
import repositories.group_repository as group_repo
import repositories.tool_repository as tool_repo

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

    layer_associations_by_id = {
        assoc.layer_id: assoc for assoc in digital_twin.layer_associations
    }

    layers_response = [
        transform_layer(layer, layer_associations_by_id.get(layer.id))
        for layer in layers
    ]

    export_data = {
        "layers": layers_response,
        "viewer": {
            "title": digital_twin.title,
            "subtitle": digital_twin.subtitle,
            **ViewerResponse.model_validate(viewer).model_dump()
        },
        "groups": [GroupResponse.model_validate(group).model_dump() for group in groups],
        "tools": [ToolResponse.model_validate(tool).model_dump() for tool in tools],
    }

    return digital_twin.name, export_data
