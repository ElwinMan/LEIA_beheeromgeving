from sqlalchemy.orm import Session
from models.tool_associations import Story

def get_by_id(db: Session, story_id: int):
    return db.query(Story).filter_by(id=story_id).first()

def get_all(db: Session):
    return db.query(Story).all()

def create(db: Session, story: Story):
    db.add(story)
    db.commit()
    db.refresh(story)
    return story

def update(db: Session, story: Story, updates: dict):
    for key, value in updates.items():
        setattr(story, key, value)
    db.commit()
    db.refresh(story)
    return story

def delete(db: Session, story_id: int):
    story = db.query(Story).filter_by(id=story_id).first()
    if story:
        db.delete(story)
        db.commit()
    return story

def get_filtered_paginated(
    db: Session,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    sort_column: str = "name",
    sort_direction: str = "asc"
):
    query = db.query(Story)
    if search:
        search_lower = f"%{search.lower()}%"
        query = query.filter(
            (Story.name.ilike(search_lower)) |
            (Story.description.ilike(search_lower))
        )
    # Sorting
    allowed_columns = ["name", "description", "id"]
    if sort_column in allowed_columns:
        sort_attr = getattr(Story, sort_column)
        if sort_direction == "desc":
            sort_attr = sort_attr.desc()
        query = query.order_by(sort_attr)
    total = query.count()
    results = query.offset((page - 1) * page_size).limit(page_size).all()
    return results, total