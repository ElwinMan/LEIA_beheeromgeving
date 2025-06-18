from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from services import digital_twin_service
from pydantic import BaseModel
from schemas.digital_twin_schema import DigitalTwinResponse

router = APIRouter(prefix="/digital_twins", tags=["Digital_twins"])

class digital_twinCreate(BaseModel):
    name: str
    title: str
    subtitle: str
    thumbnail: str

@router.get("/{digital_twin_id}", response_model=DigitalTwinResponse)
def read_digital_twin(digital_twin_id: int, db: Session = Depends(get_db)):
    digital_twin = digital_twin_service.get_digital_twin(digital_twin_id, db)
    if not digital_twin:
        raise HTTPException(status_code=404, detail="Digital_twin not found")
    return digital_twin

@router.get("/")
def read_all_digital_twins(db: Session = Depends(get_db)):
    return digital_twin_service.list_digital_twins(db)

@router.post("/")
def create_digital_twin(digital_twin: digital_twinCreate, db: Session = Depends(get_db)):
    return digital_twin_service.register_digital_twin(digital_twin.name, digital_twin.title, digital_twin.subtitle, digital_twin.thumbnail, db)
