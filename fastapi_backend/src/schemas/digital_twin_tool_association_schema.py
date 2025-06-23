from pydantic import BaseModel

class DigitalTwinToolAssociationSchema(BaseModel):
    tool_id: int

    class Config:
        orm_mode = True

class DigitalTwinToolAssociationCreate(BaseModel):
    tool_id: int