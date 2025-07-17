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
