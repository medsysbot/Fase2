
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3

router = APIRouter()
templates = Jinja2Templates(directory="templates")
DB_PATH = "static/doc/medsys.db"

@router.get("/admin/control-total", response_class=HTMLResponse)
async def control_total(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM instituciones")
    instituciones = cursor.fetchall()

    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    conn.close()

    return templates.TemplateResponse("control_total.html", {
        "request": request,
        "instituciones": instituciones,
        "usuarios": usuarios
    })

@router.post("/admin/paciente/manual/agregar")
async def agregar_paciente_manual(
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    institucion: str = Form(...),
    telefono: str = Form(...),
    email: str = Form(...)
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pacientes (nombre, apellido, dni, institucion, telefono, email)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nombre, apellido, dni, institucion, telefono, email))
    conn.commit()
    conn.close()
    return HTMLResponse(content="<script>window.location.href='/admin/control-total'</script>")


@router.get("/admin/control-total", response_class=HTMLResponse)
async def control_total(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM instituciones")
    instituciones = cursor.fetchall()

    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    cursor.execute("SELECT * FROM pacientes")
    pacientes = cursor.fetchall()

    conn.close()

    return templates.TemplateResponse("control_total.html", {
        "request": request,
        "instituciones": instituciones,
        "usuarios": usuarios,
        "pacientes": pacientes
    })
