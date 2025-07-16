from db.database import SessionLocal
from models.tool_associations import Stories
from sqlalchemy.orm import Session

def seed(db: Session):
    try:
        stories = [
            {
                "name": "My story",
                "description": "Description of my story",
                "content": {
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
                                {"id": "8352260480948"},
                                {"id": "19747667-ddb2-4162-99f6-a37d5aaa15ea", "style": "Bouwjaar"}
                            ]
                        }
                    ]
                }
            }
        ]
        for s in stories:
            if not db.query(Stories).filter_by(name=s["name"]).first():
                db.add(Stories(**s))
        db.commit()
        print("Stories seeded.")
    finally:
        db.close()

def run():
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()

if __name__ == "__main__":
    run()