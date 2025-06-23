from pydantic import BaseModel
from typing import Optional, List
from schemas.digital_twin_layer_association_schema import DigitalTwinLayerAssociationSchema
from schemas.digital_twin_tool_association_schema import DigitalTwinToolAssociationSchema

class DigitalTwinBase(BaseModel):
    name: str
    title: str
    subtitle: Optional[str] = None

class DigitalTwinCreate(DigitalTwinBase):
    pass

class DigitalTwinUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None

class DigitalTwinListResponse(DigitalTwinBase):
    id: int

    class Config:
        orm_mode = True

class DigitalTwinResponse(DigitalTwinBase):
    id: int
    layer_associations: Optional[List[DigitalTwinLayerAssociationSchema]] = []
    tool_associations: Optional[List[DigitalTwinToolAssociationSchema]] = []

    class Config:
        orm_mode = True