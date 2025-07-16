from sqlalchemy import Column, Integer, String, JSON
from db.database import Base

class Bookmarks(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    content = Column(JSON, nullable=True)

class Projects(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    content = Column(JSON, nullable=True)

class Cesium(Base):
    __tablename__ = "cesiums"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255), nullable=False)
    vertexNormals = Column(String(255), nullable=True)
    content = Column(JSON, nullable=True)

class Stories(Base):
    __tablename__ = "stories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    content = Column(JSON, nullable=True)