from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.database import Base
from models.associations import DigitalTwinLayerAssociation, DigitalTwinToolAssociation

class DigitalTwin(Base):
    __tablename__ = "digital_twin"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    subtitle = Column(String, nullable=True)

    viewer = relationship(
        "Viewer",
        back_populates="digital_twin",
        uselist=False
    )
    
    groups = relationship(
        "Group",
        back_populates="digital_twin",
        order_by="Group.sort_order",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    layer_associations = relationship(
        "DigitalTwinLayerAssociation",
        back_populates="digital_twin",
        cascade="all, delete-orphan"
    )

    layers = relationship(
        "Layer",
        secondary="digital_twin_layer_association",
        viewonly=True
    )

    tool_associations = relationship(
        "DigitalTwinToolAssociation",
        order_by="DigitalTwinToolAssociation.tool_id",
        back_populates="digital_twin",
        cascade="all, delete-orphan"
    )

    tools = relationship(
        "Tool",
        secondary="digital_twin_tool_association",
        viewonly=True
    )