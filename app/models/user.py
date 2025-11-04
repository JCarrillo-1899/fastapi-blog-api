from typing import List
from sqlmodel import SQLModel, Field, Relationship

from datetime import datetime, timezone

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relaciones
    posts: List["Post"] = Relationship(back_populates="user")
    comments: List["Comment"] = Relationship(back_populates="user")