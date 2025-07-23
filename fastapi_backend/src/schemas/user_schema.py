from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

class PaginatedUsersResponse(BaseModel):
    results: List[UserResponse]
    total: int
    page: int
    page_size: int
