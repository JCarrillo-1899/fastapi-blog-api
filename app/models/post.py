from typing import List
from sqlmodel import SQLModel, Field, Relationship

from datetime import datetime, timezone

class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    content: str
    published: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relación con user
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="posts")

    # Relación con comment
    comments: List["Comment"] = Relationship(back_populates="post")