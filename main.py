from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_303_SEE_OTHER
from auth import (
    autenticar_usuario,
    obtener_usuario_desde_cookie,
    mostrar_login,
    procesar_login,
    cerrar_sesion
)
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import json

# Inicializar FastAPI
app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar templates y archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Cargar variables de entorno
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Excepciones personalizadas
@app.exception_handler(HTTPException)
async def manejar_excepciones(request: Request, exc: HTTPException):
    if exc.status_code == 307 and "Redireccionar" in str(exc.detail):
        return RedirectResponse(url="/login")
    raise exc

# Rutas de login
@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return mostrar_login(request)

@app.post("/login", response_class=HTMLResponse)
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    return procesar_login(request, username, password)

@app.get("/logout")
def logout():
    return cerrar_sesion()

# Verificar variables de entorno (debug)
@app.get("/ver-vars")
def ver_vars():
    return {
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_KEY": bool(SUPABASE_KEY),
        "ENV": os.getenv("ENV")
    }

# Cargar jerarquía desde archivo JSON
@app.get("/jerarquia")
def obtener_jerarquia():
    json_path = os.path.join("data", "itemizado_acciona.json")
    if not os.path.exists(json_path):
        return {"error": "Archivo JSON no encontrado"}
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Página principal del formulario
@app.get("/", response_class=HTMLResponse)
def formulario(request: Request, usuario: str = Depends(obtener_usuario_desde_cookie)):
    response = templates.TemplateResponse("formulario.html", {
        "request": request,
        "mensaje": "",
        "usuario": usuario
    })
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# Registro en Supabase
@app.post("/registro", response_class=HTMLResponse)
async def registrar(
    request: Request,
    nivel1: str = Form(""),
    nivel2: str = Form(""),
    nivel3: str = Form(""),
    nivel4: str = Form(""),
    nivel5: str = Form(""),
    rp_number: str = Form(""),
    protocol_number: str = Form(""),
    status: str = Form(""),
    pk_start: str = Form(""),
    pk_end: str = Form(""),
    layer: str = Form(""),
    work_side: str = Form(""),
    thickness_m: str = Form(""),
    tag: str = Form(""),
    submission_date_pt: str = Form(""),
    approval_date_pt: str = Form(""),
    observation_notes: str = Form(""),
    usuario: str = Depends(obtener_usuario_desde_cookie)
):
    fila = {
        "nivel_1": nivel1 or "-- No Item --",
        "nivel_2": nivel2 or "-- No Item --",
        "nivel_3": nivel3 or "-- No Item --",
        "nivel_4": nivel4 or "-- No Item --",
        "nivel_5": nivel5 or "-- No Item --",
        "rp": rp_number,
        "protocolo": protocol_number,
        "estado": status,
        "pk_inicio": pk_start,
        "pk_fin": pk_end,
        "capa": layer,
        "lado": work_side,
        "espesor": thickness_m,
        "tag": tag,
        "fecha_envio": submission_date_pt,
        "fecha_aprobacion": approval_date_pt,
        "observaciones": observation_notes,
        "usuario": usuario
    }

    # Validar duplicados
    if protocol_number:
        existe_protocolo = supabase.from("registro_protocolos").select("id").eq("protocolo", protocol_number).execute()
        if existe_protocolo.data:
            return templates.TemplateResponse("formulario.html", {
                "request": request,
                "mensaje": "⚠️ Ya existe un registro con ese número de Protocolo.",
                "usuario": usuario
            })

    if rp_number:
        existe_rp = supabase.from("registro_protocolos").select("id").eq("rp", rp_number).execute()
        if existe_rp.data:
            return templates.TemplateResponse("formulario.html", {
                "request": request,
                "mensaje": "⚠️ Ya existe un registro con ese número de RP.",
                "usuario": usuario
            })

    # Insertar en Supabase
    resultado = supabase.from("registro_protocolos").insert(fila).execute()

    if resultado.error:
        return templates.TemplateResponse("formulario.html", {
            "request": request,
            "mensaje": f"❌ Error al registrar: {resultado.error.message}",
            "usuario": usuario
        })

    return templates.TemplateResponse("formulario.html", {
        "request": request,
        "mensaje": "✅ Protocolo registrado exitosamente.",
        "usuario": usuario
    })
