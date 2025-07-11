from fastapi import Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from supabase import create_client
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# --- Cargar variables del .env --- #
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ENV = os.getenv("ENV", "dev")  # dev o prod
IS_PRODUCTION = ENV == "prod"

# --- Conexión a Supabase --- #
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Seguridad para contraseñas --- #
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")

# --- Función para autenticar usuario --- #
def autenticar_usuario(username: str, password: str):
    resultado = supabase.table("usuarios").select("*").eq("username", username).execute()
    datos = resultado.data

    if not datos:
        return None

    user = datos[0]
    hash_guardado = user.get("hashed_password")

    if not pwd_context.verify(password, hash_guardado):
        return None

    return user

# --- Función para extraer usuario desde cookie (redirige si no hay login) --- #
def obtener_usuario_desde_cookie(request: Request) -> str:
    username = request.cookies.get("usuario")
    if not username:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return username

# --- Mostrar formulario login --- #
def mostrar_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "mensaje": ""})

# --- Procesar login --- #
def procesar_login(request: Request, username: str = Form(...), password: str = Form(...)):
    usuario = autenticar_usuario(username, password)
    if not usuario:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "mensaje": "❌ Usuario o contraseña incorrectos"
        })

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="usuario",
        value=username,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="Lax"
    )
    return response

# --- Logout --- #
def cerrar_sesion():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("usuario")
    return response
