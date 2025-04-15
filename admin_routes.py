from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3

router = APIRouter()
templates = Jinja2Templates(directory="templates")

DB_PATH = "static/doc/medsys.db"

@router.get("/admin-panel-super", response_class=HTMLResponse)
async def admin_panel(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, estado FROM instituciones")
    instituciones = cursor.fetchall()
    cursor.execute("SELECT usuario, rol, institucion, activo FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("admin_panel_super.html", {
        "request": request,
        "instituciones": instituciones,
        "usuarios": usuarios
    })

@router.post("/admin/usuario/activar-desactivar")
async def toggle_usuario(usuario: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT activo FROM usuarios WHERE usuario=?", (usuario,))
    current = cursor.fetchone()
    if current:
        nuevo_estado = 0 if current[0] == 1 else 1
        cursor.execute("UPDATE usuarios SET activo=? WHERE usuario=?", (nuevo_estado, usuario))
        conn.commit()
    conn.close()
    return RedirectResponse(url="/admin-panel-super", status_code=303)

@router.post("/admin/institucion/activar-desactivar")
async def toggle_institucion(institucion_id: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT estado FROM instituciones WHERE id=?", (institucion_id,))
    current = cursor.fetchone()
    if current:
        nuevo_estado = "inactiva" if current[0] == "activa" else "activa"
        cursor.execute("UPDATE instituciones SET estado=? WHERE id=?", (nuevo_estado, institucion_id))
        conn.commit()
    conn.close()
    return RedirectResponse(url="/admin-panel-super", status_code=303)
