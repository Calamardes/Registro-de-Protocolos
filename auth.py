from fastapi import Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from supabase import create_client
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from fastapi import HTTPException, status

# --- Cargar variables del .env --- #
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- Conexión a Supabase --- #
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Seguridad para contraseñas --- #
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")

# --- Mostrar Login --- #
def mostrar_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "mensaje": ""})

# --- Procesar Login --- #
def procesar_login(request: Request, username: str = Form(...), password: str = Form(...)):
    resultado = supabase.table("usuarios").select("*").eq("username", username).execute()
    datos = resultado.data

    if not datos:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "mensaje": "❌ Usuario no encontrado"
        })

    user = datos[0]
    hash_guardado = user["hashed_password"]

    if not pwd_context.verify(password, hash_guardado):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "mensaje": "❌ Contraseña incorrecta"
        })

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="usuario", value=username)
    return response

# --- Obtener Usuario desde Cookie --- #
def obtener_usuario_desde_cookie(request: Request) -> str:
    username = request.cookies.get("usuario")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="❌ No autenticado. Cookie faltante.")
    return username
