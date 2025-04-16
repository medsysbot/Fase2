from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fpdf import FPDF
import sqlite3

router = APIRouter()
templates = Jinja2Templates(directory="templates")
DB_PATH = "static/doc/medsys.db"

@router.get("/admin/pacientes", response_class=HTMLResponse)
async def panel_admin(request: Request):
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

@router.post("/admin/institucion/agregar")
async def agregar_institucion(nombre: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO instituciones (nombre, activa) VALUES (?, 1)", (nombre,))
    conn.commit()
    conn.close()
    return HTMLResponse(content="<script>window.location.href='/admin/pacientes'</script>")

@router.post("/admin/usuario/agregar")
async def agregar_usuario(usuario: str = Form(...), contrasena: str = Form(...), rol: str = Form(...), institucion: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (usuario, contrasena, rol, institucion, activo) VALUES (?, ?, ?, ?, 1)",
                   (usuario, contrasena, rol, institucion))
    conn.commit()
    conn.close()
    return HTMLResponse(content="<script>window.location.href='/admin/pacientes'</script>")
