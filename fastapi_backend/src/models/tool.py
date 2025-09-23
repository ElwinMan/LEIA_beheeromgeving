from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class Tool(Base):
    __tablename__ = "tool"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    content = Column(JSON, nullable=True)
    last_updated = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

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
