from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from db.database import Base

class Tool(Base):
    __tablename__ = "tool"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    content = Column(JSON, nullable=True)

    tool_associations = relationship(
        "DigitalTwinToolAssociation",
        back_populates="tool",
        cascade="all, delete-orphan"
    )

    digital_twins = relationship(
        "DigitalTwin",
        secondary="digital_twin_tool_association",
        viewonly=True
    )
