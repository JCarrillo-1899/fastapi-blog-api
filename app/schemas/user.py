from sqlmodel import SQLModel

class UserCreate(SQLModel):
    username: str
    email: str
    hashed_password: str

class UserResponse(SQLModel):
    id: int
    username: str
    email: str
    is_active: bool