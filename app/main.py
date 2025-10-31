from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    print("Mi API de Blogs está funcionando!")

"""Endopints Obligatorios"""
# AUTENTICACIÓN

# USUARIOS

# POSTS

# COMENTARIOS