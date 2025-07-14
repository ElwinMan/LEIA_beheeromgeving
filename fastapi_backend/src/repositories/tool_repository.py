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