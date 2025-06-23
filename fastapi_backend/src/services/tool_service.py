from sqlalchemy.orm import Session
from schemas.tool_schema import ToolCreate, ToolUpdate
import repositories.tool_repository as repo

def get_tool(tool_id: int, db: Session):
    return repo.get_tool_by_id(db, tool_id)

def list_tools(db: Session):
    return repo.get_all_tools(db)

def create_tool(tool_create: ToolCreate, db: Session):
    return repo.insert_tool(db, tool_create.dict())

def update_tool(existing_tool, tool_update: ToolUpdate, db: Session):
    return repo.update_tool(db, existing_tool, tool_update.dict())

def delete_tool(existing_tool, db: Session):
    repo.delete_tool(db, existing_tool)