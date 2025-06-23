from db.database import SessionLocal, engine
from models.tool import Tool
from sqlalchemy.orm import Session

def seed(db: Session):
    tools = [
        Tool(
            name="layerlibrary",
            content={
            "enabled": True,
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
        }),
        Tool(
            name="layermanager",
            content={
            "enabled": True,
            "settings": {}
        }),
        Tool(
            name="featureinfo",
            content={
            "enabled": True,
        }),
        Tool(
            name="info",
            content={
            "enabled": True,
            "settings": {
                "title": "Viewer title",
                "description": "Some additional information, supports <b>HTML</b>"
            }
        }),
        Tool(
            name="help",
            content={
            "enabled": True,
            "settings": {
                "showOnStart": True
            }
        }),
        Tool(
            name="bookmarks",
            content={
            "enabled": True,
            "settings": {
                "bookmarks": [
                    {
                        "title": "Heinenoordtunnel",
                        "description": "De Heinenoordtunnel is een verkeerstunnel in de Nederlandse provincie Zuid-Holland",
                        "x": 4.51056,
                        "y": 51.833003,
                        "z": 2000,
                        "heading": 0,
                        "pitch": -65,
                        "duration": 2
                    }
                ]
            }
        }),
        Tool(
            name="cesium",
            content={
            "enabled": True,
            "settings": {
                "fxaa": True,
                "shadows": False,
                "animate": False,
                "resolutionScale": 1,
                "maximumScreenSpaceError": 16,
                "groundAtmosphere": True,
                "lighting": True,
                "skyAtmosphere": True,
                "fog": True,
                "highDynamicRange": False,
                "pointCloudAttenuationMaximum": 2,
                "terrainProviders": [
                  {
                    "title": "PDOK Terrain",
                    "url": "https://api.pdok.nl/kadaster/3d-basisvoorziening/ogc/v1_0/collections/digitaalterreinmodel/quantized-mesh",
                    "vertexNormals": True
                  },
                  {
                    "title": "Uit"
                  }
                ]
            }
        }),
        Tool(
            name="stories",
            content={
            "enabled": True,
            "settings": {
                "stories": [
                    {
                        "name": "My story",
                        "description": "Description of my story",
                        "width": "600px",
                        "steps": [
                            {
                                "title": "Title of step",
                                "html": "<div>Content of the step.</div>",
                                "globeOpacity": 100,
                                "terrain": "Uit",
                                "camera": {
                                    "x": 5.23907,
                                    "y": 52.20004,
                                    "z": 13130.05823,
                                    "heading": 335.10694,
                                    "pitch": -30.69127,
                                    "duration": 1.5
                                },
                                "layers": [
                                    {
                                        "id": "8352260480948"
                                    },
                                    {
                                        "id": "19747667-ddb2-4162-99f6-a37d5aaa15ea",
                                        "style": "Bouwjaar"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }),
        Tool(
            name="measure",
            content={
            "enabled": True,
        }),
        Tool(
            name="search",
            content={
            "enabled": True,
        }),
        Tool(
            name="geocoder",
            content={
            "enabled": True,
        }),
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
