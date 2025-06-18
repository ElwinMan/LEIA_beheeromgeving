from sqlalchemy.orm import Session
from repositories import user_repository

def get_user(user_id: int, db: Session):
    return user_repository.get_user_by_id(db, user_id)

def list_users(db: Session):
    return user_repository.get_all_users(db)

def register_user(name: str, email: str, db: Session):
    return user_repository.create_user(db, name, email)