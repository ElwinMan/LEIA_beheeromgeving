from sqlalchemy.orm import Session
from models.tool import Tool
from typing import Dict, Any

def get_tool_by_id(db: Session, tool_id: int):
    return db.query(Tool).filter(Tool.id == tool_id).first()

def get_tools_by_ids(db: Session, tool_ids: list[int]):
    return db.query(Tool).filter(Tool.id.in_(tool_ids)).all()

def get_all_tools(db: Session):
    return db.query(Tool).all()

def insert_tool(db: Session, tool_data: Dict[str, Any]) -> Tool:
    tool = Tool(**tool_data)
    db.add(tool)
    db.commit()
    db.refresh(tool)
    return tool

def update_tool(db: Session, tool, updates: dict):
    for key, value in updates.items():
        setattr(tool, key, value)
    db.commit()
    db.refresh(tool)
    return tool

def delete_tool(db: Session, tool):
    db.delete(tool)
    db.commit()

def get_filtered_paginated(
    db: Session,
    search: str = "",
    page: int = 1,
    page_size: int = 10,
    sort_column: str = "name",
    sort_direction: str = "asc"
):
    query = db.query(Tool)
    if search:
        search_lower = f"%{search.lower()}%"
        query = query.filter(
            Tool.name.ilike(search_lower)
        )
    allowed_columns = ["name", "id"]
    if sort_column in allowed_columns:
        sort_attr = getattr(Tool, sort_column)
        if sort_direction == "desc":
            sort_attr = sort_attr.desc()
        query = query.order_by(sort_attr)
    total = query.count()
    results = query.offset((page - 1) * page_size).limit(page_size).all()
    return results, total