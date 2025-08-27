from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.tool_schema import ToolCreate, ToolUpdate, ToolResponse, PaginatedToolsResponse
import services.tool_service as service
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/tools", tags=["Tools"])

@router.get("/", response_model=list[ToolResponse])
def get_tools(db: Session = Depends(get_db)):
    return service.list_tools(db)

@router.get("/search", response_model=PaginatedToolsResponse)
def get_tools_search(
    db: Session = Depends(get_db),
    search: str | None = Query(None, description="Search term"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_column: str = Query("name", description="Sort column"),
    sort_direction: str = Query("asc", description="Sort direction: asc or desc")
):
    results, total = service.get_tools_filtered_paginated(
        db,
        search or "",
        page,
        page_size,
        sort_column,
        sort_direction
    )
    results = [ToolResponse.model_validate(tool, from_attributes=True) for tool in results]
    return PaginatedToolsResponse(
        results=results,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{tool_id}", response_model=ToolResponse)
def read_tool(tool_id: int, db: Session = Depends(get_db)):
    tool = service.get_tool(tool_id, db)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool

@router.post("/", response_model=ToolResponse)
def create_tool(tool: ToolCreate, db: Session = Depends(get_db)):
    try:
        return service.create_tool(tool, db)
    except IntegrityError as e:
        # Check for unique constraint violation
        if 'unique constraint' in str(e).lower() or 'duplicate key' in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail="Deze naam is al in gebruik. Kies een andere naam."
            )
        raise

@router.put("/{tool_id}", response_model=ToolResponse)
def update_tool(tool_id: int, tool_update: ToolUpdate, db: Session = Depends(get_db)):
    existing_tool = service.get_tool(tool_id, db)
    if not existing_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    try:
        return service.update_tool(existing_tool, tool_update, db)
    except IntegrityError as e:
        # Check for unique constraint violation
        if 'unique constraint' in str(e).lower() or 'duplicate key' in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail="Deze naam is al in gebruik. Kies een andere naam."
            )
        raise


@router.delete("/{tool_id}", status_code=204)
def delete_tool(tool_id: int, db: Session = Depends(get_db)):
    existing_tool = service.get_tool(tool_id, db)
    if not existing_tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    service.delete_tool(existing_tool, db)