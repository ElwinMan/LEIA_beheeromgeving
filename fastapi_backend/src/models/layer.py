from sqlalchemy import Column, Integer, String, JSON, Boolean
from sqlalchemy.orm import relationship
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

    digital_twin_associations = relationship("DigitalTwinLayerAssociation", back_populates="layer")
