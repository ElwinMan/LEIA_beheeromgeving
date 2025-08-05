from sqlalchemy import Column, Integer, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship
from db.database import Base

class DigitalTwinLayerAssociation(Base):
    __tablename__ = "digital_twin_layer_association"
    digital_twin_id = Column(Integer, ForeignKey("digital_twin.id"), primary_key=True)
    layer_id = Column(Integer, ForeignKey("layer.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("group.id"), nullable=True, default=None)
    is_default = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, nullable=False)

    digital_twin = relationship("DigitalTwin", back_populates="layer_associations")
    layer = relationship("Layer")
    group = relationship("Group")

class DigitalTwinToolAssociation(Base):
    __tablename__ = "digital_twin_tool_association"
    id = Column(Integer, primary_key=True, autoincrement=True)
    digital_twin_id = Column(Integer, ForeignKey("digital_twin.id"), nullable=False)
    tool_id = Column(Integer, ForeignKey("tool.id"), nullable=False)
    content_type_id = Column(Integer, ForeignKey("content_types.id"), nullable=True)
    content_id = Column(Integer, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    is_default = Column(Boolean, default=False, nullable=True)

    digital_twin = relationship("DigitalTwin", back_populates="tool_associations")
    tool = relationship("Tool")
    content_type = relationship("ContentType", back_populates="tool_associations")