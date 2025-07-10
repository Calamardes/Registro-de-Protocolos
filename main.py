from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from excel_handler import guardar_fila_excel
from datetime import date

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

EXCEL_PATH = "PRUEBA.xlsx"
EXCEL_SHEET = "protocol"

@app.get("/", response_class=HTMLResponse)
def formulario(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "mensaje": ""})

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
    return templates.TemplateResponse("index.html", {"request": request, "mensaje": mensaje})
