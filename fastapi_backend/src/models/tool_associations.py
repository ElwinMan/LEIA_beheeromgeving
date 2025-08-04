from sqlalchemy import Column, Integer, String, JSON, Boolean, Float
from db.database import Base

class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    z = Column(Float, nullable=False)
    heading = Column(Float, nullable=False)
    pitch = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    content = Column(JSON, nullable=True)

class TerrainProvider(Base):
    __tablename__ = "terrain_providers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    vertexNormals = Column(Boolean, nullable=True)

class Story(Base):
    __tablename__ = "stories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    content = Column(JSON, nullable=True)