from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine

from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment

# Configuración de base de datos
database_url = "postgresql://postgres:postgres@localhost:5432/Blog"
engine = create_engine(database_url, echo=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: se ejecuta al iniciar la app
    print("Creando tablas...")
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

# COMENTARIOS