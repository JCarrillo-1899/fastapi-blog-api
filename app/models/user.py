from sqlmodel import SQLModel, Field, Relationship

from datetime import datetime, timezone

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    # Relaciones
    posts = Relationship("Post", back_populates="user")
    comments = Relationship("Comment", back_populates="user")