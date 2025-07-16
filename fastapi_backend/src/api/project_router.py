from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
import services.project_service as service
from schemas.project_schema import (
    ProjectSnippetCreate,
    ProjectSnippetUpdate,
    ProjectSnippetResponse,
)

router = APIRouter(prefix="/projects-snippets", tags=["ProjectsSnippets"])

@router.get("/", response_model=list[ProjectSnippetResponse])
def get_all_snippets(db: Session = Depends(get_db)):
    return service.get_all_snippets(db)

@router.get("/{snippet_id}", response_model=ProjectSnippetResponse)
def get_snippet(snippet_id: int, db: Session = Depends(get_db)):
    snippet = service.get_snippet(db, snippet_id)
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return snippet

@router.post("/", response_model=ProjectSnippetResponse)
def create_snippet(data: ProjectSnippetCreate, db: Session = Depends(get_db)):
    return service.create_snippet(db, data)

@router.put("/{snippet_id}", response_model=ProjectSnippetResponse)
def update_snippet(snippet_id: int, data: ProjectSnippetUpdate, db: Session = Depends(get_db)):
    updated = service.update_snippet(db, snippet_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return updated

@router.delete("/{snippet_id}")
def delete_snippet(snippet_id: int, db: Session = Depends(get_db)):
    deleted = service.delete_snippet(db, snippet_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return {"detail": "Deleted"}