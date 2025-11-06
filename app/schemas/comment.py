from sqlmodel import SQLModel

class CommentCreate(SQLModel):
    content: str

class CommentResponse(SQLModel):
    id: int
    content: str