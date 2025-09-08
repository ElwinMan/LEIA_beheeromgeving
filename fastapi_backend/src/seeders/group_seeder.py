from db.database import SessionLocal
from models.group import Group
from models.digital_twin import DigitalTwin
from sqlalchemy.orm import Session

def seed(db: Session):
    # Map of digital twin names to their groups
    group_data = {
        "bodem": [
            {"title": "Bodemkaart (BRO)", "parent_id": None, "sort_order": 0},
            {"title": "Grondwaterspiegel (BRO)", "parent_id": None, "sort_order": 1},
            {"title": "GeoTOP (BRO", "parent_id": None, "sort_order": 2},
            {"title": "FRESHEM", "parent_id": None, "sort_order": 3},
            {"title": "Luchtfoto's", "parent_id": None, "sort_order": 4},
        ],
        "fier": [
            {"title": "Luchtfoto's", "parent_id": None, "sort_order": 0},
        ]
    }

    for twin_name, groups_list in group_data.items():
        digital_twin = db.query(DigitalTwin).filter_by(name=twin_name).first()
        if not digital_twin:
            print(f"Digital twin '{twin_name}' not found!")
            continue

        for group_info in groups_list:
            # Check if group already exists (based on title and digital_twin_id)
            existing = db.query(Group).filter_by(
                title=group_info["title"], 
                digital_twin_id=digital_twin.id
            ).first()
            if not existing:
                group = Group(
                    title=group_info["title"],
                    parent_id=group_info["parent_id"],
                    digital_twin_id=digital_twin.id,
                    sort_order=group_info["sort_order"],
                )
                db.add(group)
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
