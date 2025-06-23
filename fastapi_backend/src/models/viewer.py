from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from db.database import Base

class Viewer(Base):
    __tablename__ = "viewer"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(JSON, nullable=False)

    digital_twin_id = Column(Integer, ForeignKey("digital_twin.id"), unique=True)
    digital_twin = relationship("DigitalTwin", back_populates="viewer")
