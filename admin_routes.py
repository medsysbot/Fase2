from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3

router = APIRouter()
DB_PATH = "static/doc/medsys.db"
templates = Jinja2Templates(directory="templates")


@router.post("/admin/usuario/activar-desactivar")
async def activar_desactivar_usuario(usuario: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT activo FROM usuarios WHERE usuario=?", (usuario,))
    actual = cursor.fetchone()
    if actual:
        nuevo_estado = 0 if actual[0] == 1 else 1
        cursor.execute("UPDATE usuarios SET activo=? WHERE usuario=?", (nuevo_estado, usuario))
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
    return HTMLResponse(content="<script>window.location.href='/admin/pacientes'</script>")


@router.get("/exportar-pacientes/{institucion_id}")
async def exportar_pacientes(institucion_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pacientes WHERE institucion_id=?", (institucion_id,))
        pacientes = cursor.fetchall()
        conn.close()
        return {"status": "success", "pacientes": pacientes}
    except Exception as e:
        return {"status": "error", "detalle": str(e)}


@router.get("/admin/pacientes", response_class=HTMLResponse)
async def admin_pacientes(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, nombre, estado FROM instituciones")
    instituciones = cursor.fetchall()

    cursor.execute("SELECT usuario, rol, institucion, activo FROM usuarios")
    usuarios = cursor.fetchall()

    cursor.execute("SELECT id, nombre, apellido, dni, institucion, telefono, email FROM pacientes")
    pacientes = cursor.fetchall()

    conn.close()

    return templates.TemplateResponse("admin-pacientes.html", {
        "request": request,
        "instituciones": instituciones,
        "usuarios": usuarios,
        "pacientes": pacientes
    })
