from pydantic import BaseModel

class DigitalTwinLayerAssociationSchema(BaseModel):
    layer_id: int
    sort_order: int

    class Config:
        orm_mode = True