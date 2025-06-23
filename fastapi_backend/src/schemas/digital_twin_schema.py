from pydantic import BaseModel
from typing import Optional, List
from schemas.digital_twin_layer_association_schema import DigitalTwinLayerAssociationSchema

class DigitalTwinBase(BaseModel):
    name: str
    title: str
    subtitle: Optional[str] = None
    thumbnail: Optional[str] = None

class DigitalTwinCreate(DigitalTwinBase):
    pass

class DigitalTwinUpdate(BaseModel):
    name: Optional[str]
    title: Optional[str]
    subtitle: Optional[str]
    thumbnail: Optional[str]

class DigitalTwinListResponse(DigitalTwinBase):
    id: int

    class Config:
        orm_mode = True

class DigitalTwinResponse(DigitalTwinBase):
    id: int
    layer_associations: Optional[List[DigitalTwinLayerAssociationSchema]] = []

    class Config:
        orm_mode = True