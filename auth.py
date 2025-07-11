from fastapi import Request, Form, Cookie, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from supabase import create_client
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

# --- Cargar variables desde .env --- #
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- Inicializar conexión Supabase --- #
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Seguridad para contraseñas --- #
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")

# --- GET: Mostrar login --- #
def mostrar_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "mensaje": ""})

# --- POST: Procesar login --- #
def procesar_login(request: Request, username: str = Form(...), password: str = Form(...)):
    resultado = supabase.table("usuarios").select("*").eq("username", username).execute()
    datos = resultado.data

    if not datos:
        return templates.TemplateResponse("login.html", {"request": request, "mensaje": "❌ Usuario no encontrado"})

    user = datos[0]
    hash_guardado = user["hashed_password"]

    if not pwd_context.verify(password, hash_guardado):
        return templates.TemplateResponse("login.html", {"request": request, "mensaje": "❌ Contraseña incorrecta"})

    # Autenticado correctamente
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="usuario", value=username)
    return response

# --- Obtener usuario autenticado desde cookie --- #
def obtener_usuario_desde_cookie(usuario: str = Cookie(default=None)):
    if usuario is None:
        raise HTTPException(status_code=401, detail="❌ No autenticado. Cookie faltante.")
    return usuario
