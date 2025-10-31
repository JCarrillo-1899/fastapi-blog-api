from sqlmodel import SQLModel, Field

from datetime import datetime, timezone

class Comment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))