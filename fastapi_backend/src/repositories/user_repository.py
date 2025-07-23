from sqlalchemy.orm import Session
from models.user import User

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db: Session):
    return db.query(User).all()

def create_user(db: Session, user_create):
    user = User(**user_create.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user: User, user_update):
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()

def get_filtered_paginated(
    db: Session,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    sort_column: str = "name",
    sort_direction: str = "asc"
):
    query = db.query(User)
    if search:
        search_lower = f"%{search.lower()}%"
        query = query.filter(
            (User.name.ilike(search_lower)) |
            (User.email.ilike(search_lower))
        )
    allowed_columns = ["name", "email", "id"]
    if sort_column in allowed_columns:
        sort_attr = getattr(User, sort_column)
        if sort_direction == "desc":
            sort_attr = sort_attr.desc()
        query = query.order_by(sort_attr)
    total = query.count()
    results = query.offset((page - 1) * page_size).limit(page_size).all()
    return results, total
