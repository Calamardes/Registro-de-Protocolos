from fastapi import FastAPI, Request, Form, UploadFile, File, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_303_SEE_OTHER
from excel_handler import guardar_fila_excel
from auth import (
    autenticar_usuario,
    obtener_usuario_desde_cookie,
    mostrar_login,
    procesar_login,
    cerrar_sesion
)
import shutil
import os

app = FastAPI()

# --- CORS --- #
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- TEMPLATES --- #
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- LOGIN --- #
@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return mostrar_login(request)

@app.post("/login", response_class=HTMLResponse)
def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    return procesar_login(request, username, password)

# --- LOGOUT --- #
@app.get("/logout")
def logout():
    return cerrar_sesion()

# --- JERARQUÍA JSON --- #
@app.get("/jerarquia")
def obtener_jerarquia():
    json_path = os.path.join("data", "itemizado_acciona.json")
    if not os.path.exists(json_path):
        return {"error": "Archivo JSON no encontrado"}
    with open(json_path, "r", encoding="utf-8") as f:
        return f.read()

# --- FORMULARIO PRINCIPAL --- #
@app.get("/", response_class=HTMLResponse)
def formulario(request: Request, usuario: str = Depends(obtener_usuario_desde_cookie)):
    response = templates.TemplateResponse("formulario.html", {
        "request": request,
        "mensaje": "",
        "usuario": usuario
    })
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# --- REGISTRO CON ARCHIVO --- #
@app.post("/registro", response_class=HTMLResponse)
async def registrar(
    request: Request,
    archivo_excel: UploadFile = File(...),
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
    work_side: str = Form(""),
    layer: str = Form(""),
    thickness_m: str = Form(""),
    tag: str = Form(""),
    submission_date_rp: str = Form(""),
    approval_date_rp: str = Form(""),
    observation_notes: str = Form(""),
    usuario: str = Depends(obtener_usuario_desde_cookie)
):
    if not protocol_number.strip():
        return templates.TemplateResponse("formulario.html", {
            "request": request,
            "mensaje": "⚠️ Debes ingresar al menos el número de protocolo para registrar.",
            "usuario": usuario
        })

    # Guardar archivo temporal
    temp_path = f"temp_{archivo_excel.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(archivo_excel.file, buffer)

    fila = {
        "level_1": nivel1 or "-- No Item --",
        "level_2": nivel2 or "-- No Item --",
        "level_3": nivel3 or "-- No Item --",
        "level_4": nivel4 or "-- No Item --",
        "level_5": nivel5 or "-- No Item --",
        "rp_number": rp_number,
        "protocol_number": protocol_number,
        "status": status,
        "pk_start": pk_start,
        "pk_end": pk_end,
        "work_side": work_side,
        "layer": layer,
        "thickness_m": thickness_m,
        "tag": tag,
        "submission_date_rp": submission_date_rp,
        "approval_date_rp": approval_date_rp,
        "observation_notes": observation_notes,
    }

    ok, mensaje = guardar_fila_excel(temp_path, "protocol", fila)

    return templates.TemplateResponse("formulario.html", {
        "request": request,
        "mensaje": mensaje,
        "usuario": usuario
    })
