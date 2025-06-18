from sqlalchemy.orm import Session
from models.user import User

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db: Session):
    return db.query(User).all()

def create_user(db: Session, name: str, password: str, email: str):
    user = User(name=name, password=password, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
