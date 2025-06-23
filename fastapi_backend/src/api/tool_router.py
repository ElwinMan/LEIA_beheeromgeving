from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.tool_schema import ToolCreate, ToolUpdate, ToolResponse
import services.tool_service as service

router = APIRouter(prefix="/tools", tags=["Tools"])

@router.get("/", response_model=list[ToolResponse])
def get_tools(db: Session = Depends(get_db)):
    return service.list_tools(db)

@router.get("/{tool_id}", response_model=ToolResponse)
def read_tool(tool_id: int, db: Session = Depends(get_db)):
    tool = service.get_tool(tool_id, db)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool

@router.post("/", response_model=ToolResponse)
def create_tool(tool: ToolCreate, db: Session = Depends(get_db)):
    return service.create_tool(tool, db)

@router.put("/{tool_id}", response_model=ToolResponse)
def update_tool(tool_id: int, tool_update: ToolUpdate, db: Session = Depends(get_db)):
    existing_tool = service.get_tool(tool_id, db)
    if not existing_tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    return service.update_tool(existing_tool, tool_update, db)


@router.delete("/{tool_id}", status_code=204)
def delete_tool(tool_id: int, db: Session = Depends(get_db)):
    existing_tool = service.get_tool(tool_id, db)
    if not existing_tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    service.delete_tool(existing_tool, db)