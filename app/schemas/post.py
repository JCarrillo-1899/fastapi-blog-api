from sqlmodel import SQLModel

class PostCreate(SQLModel):
    title: str
    content: str

class PostResponse(SQLModel):
    id: int
    title: str
    content: str
    published: bool