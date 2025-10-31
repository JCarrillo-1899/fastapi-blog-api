from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, create_engine, select
from app.database import get_session, engine

from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment

from app.schemas.post import PostResponse, PostCreate

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

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return "Mi API de Blogs está funcionando!"

"""Endopints Obligatorios"""
# AUTENTICACIÓN

# USUARIOS

# POSTS
@app.post("/posts", response_model=PostResponse)
async def create_post(post_data: PostCreate, session: Session = Depends(get_session)):
    db_post = Post(**post_data.model_dump())

    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post

@app.get("/posts/")
async def get_posts():
    pass
# COMENTARIOS