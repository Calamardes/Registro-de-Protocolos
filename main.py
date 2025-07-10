from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from excel_handler import guardar_fila_excel
from datetime import date
import json
import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

EXCEL_PATH = "PRUEBA.xlsx"
EXCEL_SHEET = "protocol"

@app.get("/", response_class=HTMLResponse)
def formulario(request: Request):
    return templates.TemplateResponse("formulario.html", {"request": request, "mensaje": ""})

@app.post("/registro", response_class=HTMLResponse)
def registrar(
    request: Request,
    protocol_number: str = Form(...),
    status: str = Form(...),
    submission_date: str = Form(...),
    observation_notes: str = Form("")
):
    fila = {
        "protocol_number": protocol_number,
        "status": status,
        "submission_date_rp": submission_date,
        "observation_notes": observation_notes
    }

    ok, mensaje = guardar_fila_excel(EXCEL_PATH, EXCEL_SHEET, fila)
    return templates.TemplateResponse("formulario.html", {"request": request, "mensaje": mensaje})

# ✅ Ruta para entregar el JSON de jerarquía
@app.get("/jerarquia")
def obtener_jerarquia():
    json_path = os.path.join("data", "itemizado_acciona.json")
    if not os.path.exists(json_path):
        return JSONResponse(status_code=404, content={"error": "Archivo JSON no encontrado"})
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)
