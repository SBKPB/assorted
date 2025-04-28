from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class Image(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    original_filename: str
    normal_url: str
    thumbnail_url: str
    created_at: datetime = Field(default_factory=datetime.now)