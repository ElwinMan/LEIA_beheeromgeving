from db.database import SessionLocal
from models.digital_twin import DigitalTwin
from models.tool import Tool
from models.associations import DigitalTwinToolAssociation
from sqlalchemy.orm import Session

def seed(db: Session):
    # Map of digital twin names to the tool name they should be linked to
    connections = {
        "bodem": [
            "layerlibrary", 
            "layermanager",
            "featureinfo",
            "info",
            "help",
            "bookmarks",
            "cesium",
            "stories",
            "measure",
            "search",
            "geocoder",
        ],
        "fier": [
            "layerlibrary", 
            "layermanager",
            "featureinfo",
            "info",
            "help",
            "bookmarks",
            "cesium",
            "stories",
            "measure",
            "search",
            "geocoder",
        ]
    }

    for twin_name in connections:
        tool_names = connections.get(twin_name, [])
        digital_twin = db.query(DigitalTwin).filter_by(name=twin_name).first()
        if not digital_twin:
            print(f"Digital twin '{twin_name}' not found!")
            continue

        for tool_name in set(tool_names):
            tool = db.query(Tool).filter_by(name=tool_name).first()
            if not tool:
                print(f"Tool '{tool_name}' not found!")
                continue

            assoc = DigitalTwinToolAssociation(
                digital_twin_id=digital_twin.id,
                tool_id=tool.id,
            )
            db.merge(assoc)

    db.commit()
    print("Digital Twin-Tool associations seeded.")

def run():
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()

if __name__ == "__main__":
    run()
