from sqlmodel import SQLModel, Field, Relationship

from datetime import datetime, timezone

class Comment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    #user_id: int = Field(foreign_key="user.id")
    #post_id: int = Field(foreign_key="post.id")

    # Relaciones
    #user: "User" = Relationship(back_populates="comments")
    #post: "Post" = Relationship(back_populates="comments")