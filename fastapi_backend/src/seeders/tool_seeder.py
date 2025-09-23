from db.database import SessionLocal, engine
from models.tool import Tool
from sqlalchemy.orm import Session

def seed(db: Session):
    tools = [
        Tool(
            name="layerlibrary",
            description="Catalogus aan lagen die de gebruiker kan toevoegen in de viewer",
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
            description="De beheermenu in de viewer om achtergrondlagen of featurelagen te selecteren.",
        ),
        Tool(
            name="featureinfo",
            description="Feature om informatie te zien van de aangeklikte object",
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
            description="De info button, waar je de gebruiker extra informatie kan geven.",
            content={
                "settings": {
                    "title": "Viewer title",
                    "description": "Some additional information, supports <b>HTML</b>"
            }
            }
        ),
        Tool(
            name="help",
            description="De help button die je mogelijk bij het openen van de digital twin voor je ziet.",
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
            description="De bookmark functie, waarin je posities op de kaart kan bookmarken",
        ),
        Tool(
            name="cesium",
            description="Wordt gebruikt voor het inladen van de kaart en terrein.",
        ),
        Tool(
            name="stories",
            description="De story feature, waarin je posities en benodigde lagen kan selecteren en je verhaal vertellen.",
        ),
        Tool(
            name="measure",
            description="De Meetlint feature, om afstanden te meten.",
        ),
        Tool(
            name="search",
            description="De zoekbalk feature, waardoor naar steden kan zoeken.",
        ),
        Tool(
            name="geocoder",
            description="De feature die data ophaalt van steden, zodat je de search functie kan gebruiken.",
            content={
                "settings": {
                    "name": "locatieserver"
                }
            }
        ),
        Tool(
            name="projects",
            description="De feature, waardoor je een gebied kan intekenen en alleen het gebied ziet."
        ),
        Tool(
            name="flooding",
            description="De overstroming simulatie feature",
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
            description="De feature om van configuraties te switchen,",
            content={
                "settings": {
                    "fullReload": True
                }
            }
        ),
        Tool(
            name="flyCamera",
            description="De feature voor eerste persoonsperspectief door de kaart te lopen of vliegen",
        ),
        Tool(
            name="modeswitcher",
            description="De feature om van 2D en 3D te switchen",
        )
    ]

    for tool in tools:
        # Check if tool already exists
        existing = db.query(Tool).filter_by(name=tool.name).first()
        if not existing:
            db.add(tool)
    
    db.commit()
    print("Tools seeded successfully")

def run():
    db = SessionLocal()
    try:
        seed(db)
        print("Tool seeding completed!")
    finally:
        db.close()

if __name__ == "__main__":
    run()
