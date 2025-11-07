# Blog API

Una API RESTful moderna para un sistema de blogs construida con FastAPI.

## 🚀 Características

- **Autenticación JWT** - Sistema seguro de autenticación
- **CRUD Completo** - Crear, leer, actualizar y eliminar posts
- **Sistema de Comentarios** - Comentarios en posts
- **Gestión de Usuarios** - Registro y perfil de usuarios
- **Control de Accesos** - Autorización basada en ownership
- **Documentación Automática** - Swagger UI y ReDoc incluidos
- **Base de Datos SQL** - SQLModel con SQLite/PostgreSQL

## 🛠️ Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **SQLModel** - ORM para base de datos con tipado
- **JWT** - Autenticación con tokens
- **bcrypt** - Hash seguro de contraseñas
- **Uvicorn** - Servidor ASGI
- **Pydantic** - Validación de datos
- **Python 3.8+** - Lenguaje de programación

## 📋 Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🚀 Instalación Rápida

### 1. Clonar y Configurar

```bash
# Clonar el proyecto
git clone <url-del-repositorio>
cd blog-api

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```
### 2. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
DATABASE_URL=sqlite:///./blog.db
ALGORITHM=HS256
ACCESS_TOKEN_DURATION=30
```
### 3. Ejecutar la Aplicación

```bash
# Modo desarrollo con auto-recarga
uvicorn app.main:app --reload
```
### 4. Verificar Instalación

Abre tu navegador y visita:

- **Health Check:** http://localhost:8000
- **Documentación API:** http://localhost:8000/docs
- **Documentación Alternativa:** http://localhost:8000/redoc
## 🔌 Endpoints de la API

### 🔓 Endpoints Públicos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Health check de la API |
| POST | `/register` | Registrar nuevo usuario |
| POST | `/login` | Iniciar sesión y obtener token JWT |
| GET | `/posts` | Listar todos los posts publicados |
| GET | `/posts/{id}` | Obtener post específico |
| GET | `/posts/{id}/comments` | Obtener comentarios de un post |
| GET | `/users/{id}` | Obtener perfil público de usuario |
| GET | `/users/{id}/posts` | Obtener posts de un usuario específico |
### 🔐 Endpoints Protegidos (Requieren Autenticación)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/users/me` | Obtener perfil del usuario autenticado |
| PUT | `/users/me` | Actualizar perfil propio |
| POST | `/posts` | Crear nuevo post |
| PUT | `/posts/{id}` | Actualizar post (solo autor) |
| DELETE | `/posts/{id}` | Eliminar post (solo autor) |
| POST | `/posts/{id}/comments` | Crear comentario en post |
| DELETE | `/comments/{id}` | Eliminar comentario (solo autor) |
## 🔑 Autenticación

### 1. Registro de Usuario

```bash
curl -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "mi_usuario",
       "email": "usuario@ejemplo.com", 
       "hashed_password": "mi_contraseña_segura"
     }'
```
### 2. Login y Obtención de Token

```bash
curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=mi_usuario&password=mi_contraseña_segura"
```
**Respuesta:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```
### 3. Usar Token en Requests

```bash
curl -X GET "http://localhost:8000/users/me" \
     -H "Authorization: Bearer <tu-token-jwt>"
```
## 💾 Modelos de Datos

### User
- `id: int` (Primary Key)
- `username: str` (único)
- `email: str` (único)
- `hashed_password: str`
- `is_active: bool = True`
- `created_at: datetime`

### Post
- `id: int` (Primary Key)
- `title: str`
- `content: str`
- `published: bool = True`
- `created_at: datetime`
- `user_id: int` (Foreign Key a User)

### Comment
- `id: int` (Primary Key)
- `content: str`
- `created_at: datetime`
- `user_id: int` (Foreign Key a User)
- `post_id: int` (Foreign Key a Post)
## 🧪 Ejemplos de Uso

### Crear un Post

```bash
curl -X POST "http://localhost:8000/posts" \
     -H "Authorization: Bearer <tu-token>" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Mi primer post",
       "content": "Este es el contenido de mi primer post...",
       "published": true
     }'
```
### Crear un Comentario

```bash
curl -X POST "http://localhost:8000/posts/1/comments" \
     -H "Authorization: Bearer <tu-token>" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Este es un comentario interesante!"
     }'
```
### Actualizar Perfil de Usuario

```bash
curl -X PUT "http://localhost:8000/users/me" \
     -H "Authorization: Bearer <tu-token>" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "nuevo_email@ejemplo.com"
     }'
```
## 📈 Próximos Pasos

Para llevar este proyecto al siguiente nivel considera:

1. **Implementar refresh tokens**
2. **Agregar sistema de roles y permisos**
3. **Implementar paginación en endpoints de listas**
4. **Agregar upload de imágenes**
5. **Implementar sistema de likes/favoritos**
6. **Agregar tests automatizados**

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

---

**¡Listo para empezar!** 🎉 Ejecuta `uvicorn app.main:app --reload` y visita `http://localhost:8000/docs` para explorar la API.
