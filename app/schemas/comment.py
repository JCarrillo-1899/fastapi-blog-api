from sqlmodel import SQLModel

class PostCreate(SQLModel):
    content: str

class PostResponse(SQLModel):
    id: int
    content: str