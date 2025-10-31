from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine

from models.user import User
from models.post import Post
from models.comment import Comment

# Creando las tablas
database_url = "postgresql://postgres:postgres@localhost:5432/Blog"
engine = create_engine(database_url, echo=True)
SQLModel.metadata.create_all(engine)

app = FastAPI()

@app.get("/")
def root():
    return "Mi API de Blogs está funcionando!"

"""Endopints Obligatorios"""
# AUTENTICACIÓN

# USUARIOS

# POSTS

# COMENTARIOS