from sqlmodel import SQLModel, Field, Relationship

from datetime import datetime, timezone

class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    content: str
    published: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    # Relación con user
    author_id: int = Field(foreign_key="user.id")
    user = Relationship("User", back_populates="posts")

    # Relación con comment
    comments = Relationship("Comment", back_populates="post")