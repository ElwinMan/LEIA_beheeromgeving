from sqlalchemy.orm import Session
import repositories.content_type_repository as repo
from models.content_type import ContentType
from schemas.content_type_schema import ContentTypeCreate, ContentTypeUpdate

def get_content_type(db: Session, content_type_id: int) -> ContentType | None:
    return repo.get_by_id(db, content_type_id)

def get_content_type_by_name(db: Session, name: str) -> ContentType | None:
    return repo.get_by_name(db, name)

def get_all_content_types(db: Session) -> list[ContentType]:
    return repo.get_all(db)

def create_content_type(db: Session, data: ContentTypeCreate) -> ContentType:
    content_type = ContentType(**data.dict())
    return repo.create(db, content_type)

def update_content_type(db: Session, content_type_id: int, updates: ContentTypeUpdate) -> ContentType | None:
    content_type = repo.get_by_id(db, content_type_id)
    if not content_type:
        return None
    return repo.update(db, content_type, updates.dict(exclude_unset=True))

def delete_content_type(db: Session, content_type_id: int) -> bool:
    return repo.delete(db, content_type_id)
