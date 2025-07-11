from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from supabase import create_client
from passlib.context import CryptContext
import os

# --- Configuración inicial --- #
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Configuración de Supabase --- #
SUPABASE_URL = "https://vigeeusnyypmklbxspoa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZpZ2VldXNueXlwbWtsYnhzcG9hIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjIwMDk4NCwiZXhwIjoyMDY3Nzc2OTg0fQ.Gj4247w9h7zM87CP4_gQk6BnSgcnsykcv97NajMj6N0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Configuración de contraseña segura --- #
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Rutas --- #

@app.get("/login", response_class=HTMLResponse)
def mostrar_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "mensaje": ""})


@app.post("/login", response_class=HTMLResponse)
def procesar_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    # Buscar usuario en Supabase
    resultado = supabase.table("usuarios").select("*").eq("username", username).execute()
    datos = resultado.data

    if not datos:
        return templates.TemplateResponse("login.html", {"request": request, "mensaje": "❌ Usuario no encontrado"})

    user = datos[0]
    hash_guardado = user["hashed_password"]

    if not pwd_context.verify(password, hash_guardado):
        return templates.TemplateResponse("login.html", {"request": request, "mensaje": "❌ Contraseña incorrecta"})

    # Usuario autenticado con éxito
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="usuario", value=username)  # Cookie básica por ahora
    return response
