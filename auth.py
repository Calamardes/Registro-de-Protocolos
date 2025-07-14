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

# --- Mostrar en consola para depuración --- #
print(f"🔎 SUPABASE_URL: {SUPABASE_URL}")
print(f"🔑 SUPABASE_KEY cargada: {bool(SUPABASE_KEY)}")
print(f"🌍 Modo: {'Producción' if IS_PRODUCTION else 'Desarrollo'}")

# --- Validación mínima --- #
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Variables SUPABASE_URL o SUPABASE_KEY no están definidas.")

# --- Conexión a Supabase --- #
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Seguridad para contraseñas --- #
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")

# --- Autenticación --- #
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

# --- Verificar cookie o lanzar excepción --- #
def obtener_usuario_desde_cookie(request: Request) -> str:
    username = request.cookies.get("usuario")
    if not username:
        raise HTTPException(status_code=307, detail="Redireccionar al login")
    return username

# --- Mostrar formulario login --- #
def mostrar_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "mensaje": ""})

# --- Procesar login con manejo de errores --- #
def procesar_login(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
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

    except Exception as e:
        print(f"🚨 Error al procesar login: {e}")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "mensaje": f"❌ Error interno: {str(e)}"
        })

# --- Logout --- #
def cerrar_sesion():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("usuario")
    return response
