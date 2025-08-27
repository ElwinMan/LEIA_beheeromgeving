from pydantic import BaseModel, field_serializer
from typing import Optional, List
from datetime import datetime
from schemas.digital_twin_layer_association_schema import DigitalTwinLayerAssociationSchema, DigitalTwinLayerBulkOperation
from schemas.digital_twin_tool_association_schema import DigitalTwinToolAssociationSchema
from schemas.group_schema import DigitalTwinGroupBulkOperation

class DigitalTwinBase(BaseModel):
    name: str
    title: str
    subtitle: Optional[str] = None
    owner: Optional[str] = None
    private: bool
    last_updated: datetime

    @field_serializer("last_updated")
    def format_last_updated(self, value: datetime) -> str:
        return value.isoformat()

class DigitalTwinCreate(DigitalTwinBase):
    pass

class DigitalTwinUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None
    owner: Optional[str] = None
    private: Optional[bool] = None

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


class BulkAssociationsPayload(BaseModel):
    layer_payload: DigitalTwinLayerBulkOperation
    group_payload: DigitalTwinGroupBulkOperation

class DigitalTwinSummary(BaseModel):
    id: int
    name: str
    title: str

    class Config:
        orm_mode = True

class PaginatedDigitalTwinResponse(BaseModel):
    results: List[DigitalTwinListResponse]
    total: int
    page: int
    page_size: int

