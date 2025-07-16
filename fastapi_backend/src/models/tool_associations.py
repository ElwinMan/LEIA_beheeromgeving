from sqlalchemy import Column, Integer, String, JSON
from db.database import Base

class BookmarksSnippets(Base):
    __tablename__ = "bookmarksSnippets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    content = Column(JSON, nullable=True)

class ProjectsSnippets(Base):
    __tablename__ = "projectsSnippets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    content = Column(JSON, nullable=True)

class TerrainProvidersSnippets(Base):
    __tablename__ = "terrainProvidersSnippets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255), nullable=False)
    vertexNormals = Column(String(255), nullable=True)
    content = Column(JSON, nullable=True)

class StoriesSnippets(Base):
    __tablename__ = "storiesSnippets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    content = Column(JSON, nullable=True)