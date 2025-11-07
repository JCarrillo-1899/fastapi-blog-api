import jwt
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Session, create_engine, select
from app.database import get_session, engine
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError

from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment

from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.post import PostResponse, PostCreate
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.schemas.token import Token

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # ✅ CREA tablas nuevas con la estructura actual
    print("Creando tablas nuevas...")
    SQLModel.metadata.create_all(engine)
    
    yield

    # Shutdown: se ejecuta al cerrar la app
    print("Cerrando conexiones...")

# CONFIGURACIÓN JWT Y SEGURIDAD
ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 10
SECRET = "4b0cf6bf3a6fbc48ad681a508e4aae525eb376a640f0145f56975064fc26a4ae"

app = FastAPI(lifespan=lifespan)

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- FUNCIONES DE UTILIDAD ---
def search_user(username: str, session: Session):
    """Busca usuario por username y verifica si está activo"""

    statement = select(User).where(User.username==username)
    
    response = session.exec(statement).first()
    if not response:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrecta")
    
    if not response.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Usuario inactivo")

    return response

def verify_user_by_id(id: int, session: Session):
    """Verifica si un usuario existe por ID"""

    statement = select(User).where(User.id==id)
    response = session.exec(statement).first()

    return response

def verify_post_by_id(id: int, session: Session):
    """Verifica si un post publicado existe por ID"""

    statement = select(Post).where(Post.published==True).where(Post.id==id)
    response = session.exec(statement).first()

    return response

def verify_comment_by_id(id: int, session: Session):
    """Verifica si un comentario existe por ID"""

    statement = select(Comment).where(Comment.id==id)
    response = session.exec(statement).first()

    return response

def verify_password(password: str, hashed_apssword: str):
    """Verifica si password coincide con hash"""

    return crypt.verify(password, hashed_apssword)

def hash_password(password: str):
    """Genera hash seguro de password"""

    return crypt.hash(password)

def create_access_token(data: dict):
    """Crea JWT token con expiración"""

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_DURATION)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)

    return encoded_jwt

async def get_current_user(
        token: Annotated[str, Depends(oauth2)], 
        session: Annotated[Session, Depends(get_session)]):
    """Dependencia para obtener usuario actual desde JWT"""

    exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciales de autenticación inválidas", 
            headers={"WWW-Authenticate": "Bearer"}
            )
    
    try:
        username = jwt.decode(token, SECRET, algorithms=ALGORITHM).get("sub")
        if username is None:
            raise exception
    except InvalidTokenError:
        raise exception
    
    return search_user(username, session)

# --- ENDPOINTS ---
@app.get("/")
def root():
    """Health check - verifica que API esté funcionando"""
    return "Mi API de Blogs está funcionando!"

# AUTENTICACIÓN
@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, session: Annotated[Session, Depends(get_session)]):
    """Registra nuevo usuario en el sistema"""

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
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[Session, Depends(get_session)]):
    """Autentica usuario y devuelve JWT token"""

    user_db = search_user(form.username, session)
    password = verify_password(form.password, user_db.hashed_password)
    
    if not (user_db and password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrecta")
    
    access_token = create_access_token(data={"sub": user_db.username, "user_id": user_db.id})
    
    return Token(access_token=access_token, token_type="bearer")

# USUARIOS
@app.get("/users/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Obtiene perfil del usuario autenticado"""
    
    return current_user

@app.put("/users/me", response_model=UserResponse)
async def update_user(
    form_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)], 
    session: Annotated[Session, Depends(get_session)]
    ):
    """Actualiza perfil del usuario autenticado"""

    if form_data.email is not None:
        current_user.email = form_data.email
    
    if form_data.is_active is not None:
        current_user.is_active = form_data.is_active
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return current_user

@app.get("/users/{id}", response_model=UserResponse)
async def get_user_by_id(id: int, session: Annotated[Session, Depends(get_session)]):
    """Obtiene perfil público de usuario por ID"""

    response = verify_user_by_id(id, session)

    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe un usuario con ese ID")

    return response

@app.get("/users/{id}/posts", response_model=list[PostResponse])
async def get_user_posts(id: int, session: Annotated[Session, Depends(get_session)]):
    """Obtiene todos los posts de un usuario específico"""
    
    if not verify_user_by_id(id, session):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe un usuario con ese ID")
    
    statement = select(Post).where(Post.user_id==id)
    response = session.exec(statement).all()

    return response

# POSTS
@app.post("/posts", response_model=PostResponse)
async def create_post(
    post_data: PostCreate, 
    current_user: Annotated[User, Depends(get_current_user)], 
    session: Annotated[Session, Depends(get_session)]
    ):
    """Crea nuevo post (requiere autenticación)"""
    
    db_post = Post(**post_data.model_dump(), user_id=current_user.id)

    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post

@app.get("/posts", response_model=list[PostResponse])
async def get_posts(session: Annotated[Session, Depends(get_session)]):
    """Obtiene todos los posts publicados"""

    statement = select(Post).where(Post.published==True)
    response = session.exec(statement).all()
    return response

@app.get("/posts/{id}", response_model=PostResponse)
async def get_post_by_id(id: int, session: Annotated[Session, Depends(get_session)]):
    """Obtiene post específico por ID"""
    
    response = verify_post_by_id(id, session)

    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encuentra un post con ese ID")

    return response

@app.put("/posts/{id}", response_model=PostResponse)
async def update_post(
    id: int, 
    post_data: PostCreate,
    current_user: Annotated[User, Depends(get_current_user)], 
    session: Annotated[Session, Depends(get_session)]
    ):
    """Actualiza post existente (solo autor)"""

    response = verify_post_by_id(id, session)

    if not response:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    
    if response.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para editar este post")
    

    response.title = post_data.title
    response.content = post_data.content

    session.add(response)
    session.commit()
    session.refresh(response)

    return response

@app.delete("/posts/{id}")
async def delete_post_by_id(
    id: int, 
    current_user: Annotated[User, Depends(get_current_user)], 
    session: Annotated[Session, Depends(get_session)]
    ):
    """Elimina post (solo autor)"""

    response = verify_post_by_id(id, session)
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")
    
    if response.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para editar este post")
    
    session.delete(response)
    session.commit()

    return {"message": "Post eliminado correctamente"}

# COMENTARIOS

@app.post("/posts/{id}/comments", response_model=CommentResponse)
async def create_comment(
    id: int, 
    comment: CommentCreate, 
    current_user: Annotated[User, Depends(get_current_user)], 
    session: Annotated[Session, Depends(get_session)]
    ):
    """Crea comentario en post específico"""

    post = verify_post_by_id(id, session)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")
    
    db_comment = Comment(**comment.model_dump(), user_id=current_user.id, post_id=id)

    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)

    return db_comment

@app.get("/posts/{id}/comments", response_model=list[CommentResponse])
async def get_post_comments(id: int, session: Annotated[Session, Depends(get_session)]):
    """Obtiene todos los comentarios de un post"""

    if not verify_post_by_id(id, session):
        raise HTTPException(status_code=404, detail="Post no encontrado")
    
    statement = select(Comment).where(Comment.post_id == id)
    comments = session.exec(statement).all()
    return comments

@app.delete("/comments/{id}")
async def delete_comment(
    id: int, 
    current_user: Annotated[User, Depends(get_current_user)], 
    session: Annotated[Session, Depends(get_session)]
    ):
    """Elimina comentario (solo autor)"""
    
    comment = verify_comment_by_id(id, session)

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe un comentario con ese ID")
    
    # Verificar que el usuario es el autor del comentario
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    session.delete(comment)
    session.commit()
    return {"message": "Comentario eliminado"}