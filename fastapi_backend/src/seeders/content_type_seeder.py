from sqlalchemy.orm import Session
from sqlalchemy import text
from db.database import SessionLocal
from models.content_type import ContentType

def seed(db: Session):
    content_types = [
        ContentType(name="bookmark", table_name="bookmarks"),
        ContentType(name="project", table_name="projects"),
        ContentType(name="story", table_name="stories"),
        ContentType(name="terrain_provider", table_name="terrain_providers"),
    ]
    
    for content_type in content_types:
        existing = db.query(ContentType).filter_by(name=content_type.name).first()
        if not existing:
            db.add(content_type)
    
    db.commit()
    print("Content types seeded successfully")

def run():
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()

if __name__ == "__main__":
    run()
