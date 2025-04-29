from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class Image(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    album_id: UUID = Field(foreign_key="album.id", nullable=False)
    original_filename: str
    normal_url: str
    thumbnail_url: str
    created_at: datetime = Field(default_factory=datetime.now)


class ImagePublic(BaseModel):
    id: UUID
    album_id: UUID
    original_filename: str
    normal_url: str
    thumbnail_url: str
    created_at: datetime
