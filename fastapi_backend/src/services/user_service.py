from sqlalchemy.orm import Session
import repositories.user_repository as repo
from schemas.user_schema import UserCreate, UserUpdate

def get_user(user_id: int, db: Session):
    return repo.get_user_by_id(db, user_id)

def list_users(db: Session):
    return repo.get_all_users(db)

def create_user(user_create: UserCreate, db: Session):
    return repo.create_user(db, user_create)

def update_user(existing_user, user_update: UserUpdate, db: Session):
    return repo.update_user(db, existing_user, user_update)

def delete_user(existing_user, db: Session):
    return repo.delete_user(db, existing_user)

def get_users_filtered_paginated(
    db: Session,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    sort_column: str = "name",
    sort_direction: str = "asc"
):
    return repo.get_filtered_paginated(
        db,
        search,
        page,
        page_size,
        sort_column,
        sort_direction
    )