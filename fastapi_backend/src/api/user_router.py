from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from services import user_service
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["Users"])

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

@router.get("/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get_user(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/")
def read_all_users(db: Session = Depends(get_db)):
    return user_service.list_users(db)

@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_service.register_user(user.name, user.password, user.email, db)
