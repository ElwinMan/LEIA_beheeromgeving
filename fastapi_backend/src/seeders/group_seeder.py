from db.database import SessionLocal
from models.group import Group
from sqlalchemy.orm import Session

def seed(db: Session):
    groups = [
        Group(
            title="Bodemkaart (BRO)",
            parent_id=None,
            digital_twin_id=1,
            sort_order=0,
        ),
        Group(
            title="Grondwaterspiegel (BRO)",
            parent_id=None,
            digital_twin_id=1,
            sort_order=1,
        ),
        Group(
            title="GeoTOP (BRO",
            parent_id=None,
            digital_twin_id=1,
            sort_order=2,
        ),
        Group(
            title="FRESHEM",
            parent_id=None,
            digital_twin_id=1,
            sort_order=3,
        ),
        Group(
            title="Luchtfoto's",
            parent_id=None,
            digital_twin_id=1,
            sort_order=4,
        ),
        Group(
            title="Luchtfoto's",
            parent_id=None,
            digital_twin_id=2,
            sort_order=0,
        )
    ]

    db.add_all(groups)
    db.commit()

def run():
    db = SessionLocal()
    try:
        seed(db)
        print("Group seeding completed!")
    finally:
        db.close()

if __name__ == "__main__":
    run()
