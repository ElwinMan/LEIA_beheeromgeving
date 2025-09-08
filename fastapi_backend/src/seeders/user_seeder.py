from db.database import SessionLocal, engine
from models.user import User
from sqlalchemy.orm import Session

def seed(db: Session):
    users = [
        User(name="Alice", password='test', email="alice@example.com"),
        User(name="Bob", password='test', email="bob@example.com"),
    ]

    for user in users:
        # Check if user already exists
        existing = db.query(User).filter_by(email=user.email).first()
        if not existing:
            db.add(user)
    db.commit()

def run():
    db = SessionLocal()
    try:
        seed(db)
        print("User seeding completed!")
    finally:
        db.close()

if __name__ == "__main__":
    run()
