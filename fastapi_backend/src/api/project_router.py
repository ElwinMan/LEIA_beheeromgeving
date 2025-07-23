from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import get_db
import services.project_service as service
from schemas.project_schema import (
    PaginatedProjectsResponse,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/", response_model=list[ProjectResponse])
def get_all_projects(db: Session = Depends(get_db)):
    return service.get_all_projects(db)

@router.get("/search", response_model=PaginatedProjectsResponse)
def get_projects_search(
    db: Session = Depends(get_db),
    search: str | None = Query(None, description="Search term"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_column: str = Query("name", description="Sort column"),
    sort_direction: str = Query("asc", description="Sort direction: asc or desc")
):
    results, total = service.get_projects_filtered_paginated(
        db,
        search or "",
        page,
        page_size,
        sort_column,
        sort_direction
    )
    results = [ProjectResponse.model_validate(project, from_attributes=True) for project in results]
    return PaginatedProjectsResponse(
        results=results,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/", response_model=ProjectResponse)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    return service.create_project(db, data)

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    updated = service.update_project(db, project_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    deleted = service.delete_project(db, project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"detail": "Deleted"}