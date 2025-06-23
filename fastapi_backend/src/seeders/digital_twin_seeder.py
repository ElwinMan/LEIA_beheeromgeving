from db.database import SessionLocal, engine
from models.digital_twin import DigitalTwin
from sqlalchemy.orm import Session

def seed(db: Session):
    digital_twins = [
        DigitalTwin(name="bodem", title="Klimaat Scenario", subtitle="Bodem"),
        DigitalTwin(name="fier", title="Leia viewer", subtitle="Overstroming en mobiliteit"),
    ]

    for digital_twin in digital_twins:
        db.add(digital_twin)
    db.commit()

def run():
    db = SessionLocal()
    try:
        seed(db)
        print("Digital Twin Seeding completed!")
    finally:
        db.close()

if __name__ == "__main__":
    run()
