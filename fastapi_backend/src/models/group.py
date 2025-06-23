from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class Group(Base):
    __tablename__ = "group"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    digital_twin_id = Column(Integer, ForeignKey("digital_twin.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("group.id"), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)

    digital_twin = relationship("DigitalTwin", back_populates="groups")
    children = relationship("Group", backref="parent", remote_side=[id])


