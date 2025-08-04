from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.database import Base

class ContentType(Base):
    __tablename__ = "content_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    table_name = Column(String, nullable=False)

    tool_associations = relationship(
        "DigitalTwinToolAssociation",
        back_populates="content_type"
    )
