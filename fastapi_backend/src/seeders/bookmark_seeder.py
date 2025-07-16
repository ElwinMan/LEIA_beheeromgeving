from db.database import SessionLocal
from models.tool_associations import BookmarksSnippets
from sqlalchemy.orm import Session

def seed(db: Session):
    try:
        bookmarks_snippets = [
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
        for b in bookmarks_snippets:
            if not db.query(BookmarksSnippets).filter_by(title=b["title"]).first():
                db.add(BookmarksSnippets(**b))
        db.commit()
        print("Bookmarks snippets seeded.")
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