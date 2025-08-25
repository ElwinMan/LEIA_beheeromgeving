from db.database import SessionLocal, engine
from models.tool import Tool
from sqlalchemy.orm import Session

def seed(db: Session):
    tools = [
        Tool(
            name="layerlibrary",
            content={
                "settings": {
                    "connectors": [
                        {
                            "type": "ckan",
                            "url": "https://data.beta.geodan.nl",
                            "organizations": [
                                "rijkswaterstaat",
                                "pdok"
                            ],
                            "groups": [
                                "group_name_1",
                                "group_name_2",
                                "group_name_3"
                            ],
                            "packages": [
                                "package_name_1",
                                "package_name_2"
                            ],
                            "specialResources": {
                                "backgroundLayers": [
                                    "resource_name_1",
                                    "fd1126fd-c557-47e6-9d95-e60d5897eeb0"
                                ],
                                "layersAddedOn": [
                                    "7f7b7023-225f-4018-ae4a-3381c79c7248"
                                ],
                                "layersAddedOff": [
                                    "resource_name_2"
                                ]
                            }
                        }
                    ],
                    "useTags": True
                }
            }
        ),
        Tool(
            name="layermanager",
        ),
        Tool(
            name="featureinfo",
            content= {
                "fields": [{
                        "field": "image",
                        "handler": "image"
                    },
                    {
                        "field": "document",
                        "handler": "pdf"
                    },
                    {
                        "field": "plot",
                        "handler": "chart"
                    }
                ]
            }
        ),
        Tool(
            name="info",
            content={
                "settings": {
                    "title": "Viewer title",
                    "description": "Some additional information, supports <b>HTML</b>"
            }
            }
        ),
        Tool(
            name="help",
            content={
                    "settings": {
                        "title": "title",
                        "intro": "<img style='float: right;max-width: 15rem' src='https://www.image.domain/my_image.jpg' /> <div class='body-02'>Some contextual information.</div>",
                        "showOnStart": True
                }
            }
        ),
        Tool(
            name="bookmarks",
        ),
        Tool(
            name="cesium",
        ),
        Tool(
            name="stories",
        ),
        Tool(
            name="measure"
        ),
        Tool(
            name="search"
        ),
        Tool(
            name="geocoder"
        ),
        Tool(
            name="projects"
        ),
        Tool(
            name="flooding",
            content={
                "settings": {
                    "scenariosBaseUrl": "https://virtueel.zeeland.nl/tiles_other/overstroming/",
                    "breachUrl": "https://virtueel.zeeland.nl/tiles_other/breslocaties.geojson",
                    "roadsUrl": "https://service.pdok.nl/rws/vervoersnetwerken/wegen/wms/v1_0",
                    "floodedRoadsUrl": "https://virtueel.zeeland.nl/pygeoapi",
                    "floodedRoadsStyle": [
                        {
                            "property": "flood_depth",
                            "stops": [
                                {
                                    "value": 0,
                                    "color": "#ffff00"
                                },
                                {
                                    "value": 3,
                                    "color": "#ff0000"
                                }
                            ]
                        }
                    ]
                }
            }
        ),
        Tool(
            name="config_switcher",
            content={
                "settings": {
                    "fullReload": True
                }
            }
        ),
        Tool(
            name="flyCamera"
        ),
        Tool(
            name="modeswitcher"
        )
    ]

    for tool in tools:
        db.add(tool)
    db.commit()

def run():
    db = SessionLocal()
    try:
        seed(db)
        print("Tool seeding completed!")
    finally:
        db.close()

if __name__ == "__main__":
    run()
