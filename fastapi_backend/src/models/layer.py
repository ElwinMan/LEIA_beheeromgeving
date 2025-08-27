from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class Layer(Base):
    __tablename__ = "layer"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    beschrijving = Column(String, nullable=True)
    url = Column(String, nullable=False)
    featureName = Column(String, nullable=True)
    isBackground= Column(Boolean, default=False)
    content = Column(JSON, nullable=True)
    last_updated = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    digital_twin_associations = relationship("DigitalTwinLayerAssociation", back_populates="layer")
