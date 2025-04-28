from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

class Album(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.now)


class AlbumCreate(BaseModel):
    name: str


class AlbumUpdate(BaseModel):
    name: str


class AlbumPublic(BaseModel):
    id: UUID
    name: str
    created_at: datetime
