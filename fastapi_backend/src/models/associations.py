from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class DigitalTwinLayerAssociation(Base):
    __tablename__ = "digital_twin_layer_association"
    digital_twin_id = Column(Integer, ForeignKey("digital_twin.id"), primary_key=True)
    layer_id = Column(Integer, ForeignKey("layer.id"), primary_key=True)
    sort_order = Column(Integer, nullable=False)

    digital_twin = relationship("DigitalTwin", back_populates="layer_associations")
    layer = relationship("Layer")

class DigitalTwinToolAssociation(Base):
    __tablename__ = "digital_twin_tool_association"
    digital_twin_id = Column(Integer, ForeignKey("digital_twin.id"), primary_key=True)
    tool_id = Column(Integer, ForeignKey("tool.id"), primary_key=True)
    sort_order = Column(Integer, nullable=False)

    digital_twin = relationship("DigitalTwin", back_populates="tool_associations")
    tool = relationship("Tool")
