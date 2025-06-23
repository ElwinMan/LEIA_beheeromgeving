from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
import services.user_service as service
from schemas.user_schema import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = service.get_user(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=list[UserResponse])
def read_all_users(db: Session = Depends(get_db)):
    return service.list_users(db)

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return service.create_user(user, db)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    existing_user = service.get_user(user_id, db)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    return service.update_user(existing_user, user_update, db)

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    existing_user = service.get_user(user_id, db)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    service.delete_user(existing_user, db)
