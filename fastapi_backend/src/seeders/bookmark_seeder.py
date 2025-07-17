from db.database import SessionLocal
from models.tool_associations import Bookmark
from sqlalchemy.orm import Session

def seed(db: Session):
    try:
        bookmarks = [
            {
                "title": "Heinenoordtunnel",
                "description": "Bookmark set for Heinenoordtunnel",
                "content": [
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
        ]
        for b in bookmarks:
            if not db.query(Bookmark).filter_by(title=b["title"]).first():
                db.add(Bookmark(**b))
        db.commit()
        print("Bookmarks seeded.")
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