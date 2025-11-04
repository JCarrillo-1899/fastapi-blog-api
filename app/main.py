import jwt
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Session, create_engine, select
from app.database import get_session, engine
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment

from app.schemas.post import PostResponse, PostCreate
from app.schemas.user import UserResponse, UserCreate
from app.schemas.token import Token

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ ELIMINA tablas existentes
    print("Eliminando tablas antiguas...")
    SQLModel.metadata.drop_all(engine)
    
    # ✅ CREA tablas nuevas con la estructura actual
    print("Creando tablas nuevas...")
    SQLModel.metadata.create_all(engine)
    
    yield

    # Shutdown: se ejecuta al cerrar la app
    print("Cerrando conexiones...")

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1
SECRET = "4b0cf6bf3a6fbc48ad681a508e4aae525eb376a640f0145f56975064fc26a4ae"

app = FastAPI(lifespan=lifespan)

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])

def search_user(username: str, session: Session):
    statement = select(User).where(User.username==username)
    
    response = session.exec(statement).first()
    if not response:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrecta")
    
    if not response.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Usuario inactivo")

    return response

def verify_password(password: str, hashed_apssword: str):
    return crypt.verify(password, hashed_apssword)

def hash_password(password: str):
    return crypt.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_DURATION)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)

    return encoded_jwt

@app.get("/")
def root():
    return "Mi API de Blogs está funcionando!"

"""Endopints Obligatorios"""
# AUTENTICACIÓN
@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, session: Session = Depends(get_session)):

    statement = select(User).where(User.email==user.email)
    response = session.exec(statement).all()
    if response:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un usuario con ese email")

    statement = select(User).where(User.username==user.username)
    response = session.exec(statement).all()
    if response:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un usuario con ese nombre")

    user_data = user.model_dump(exclude={"hashed_password"})
    hashed_pass = hash_password(user.hashed_password)

    db_user = User(**user_data, hashed_password=hashed_pass)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.post("/login", response_model=Token)
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_session)):
    
    user_db = search_user(form.username, session)
    password = verify_password(form.password, user_db.hashed_password)
    
    if not (user_db and password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrecta")
    
    access_token = create_access_token(data={"sub": user_db.username, "user_id": user_db.id})
    
    return Token(access_token=access_token, token_type="bearer")

# USUARIOS

# POSTS
@app.post("/posts", response_model=PostResponse)
async def create_post(post_data: PostCreate, session: Session = Depends(get_session)):
    db_post = Post(**post_data.model_dump())

    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post

@app.get("/posts", response_model=list[PostResponse])
async def get_posts(session: Session= Depends(get_session)):
    statement = select(Post).where(Post.published==True)
    response = session.exec(statement).all()
    return response

@app.get("/posts/{id}", response_model=PostResponse)
async def get_post_by_id(id: int, session: Session = Depends(get_session)):
    try:
        statement = select(Post).where(Post.published==True).where(Post.id==id)
        response = session.exec(statement).one()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encuentra un post con ese ID")
    return response
# COMENTARIOS