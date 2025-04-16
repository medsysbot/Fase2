from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from fpdf import FPDF
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")
DB_PATH = "static/doc/medsys.db"

# ---------------- PANEL /admin/pacientes ----------------
@router.get("/admin/pacientes", response_class=HTMLResponse)
async def admin_pacientes(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Cargar instituciones
    try:
        cursor.execute("SELECT id, nombre, estado FROM instituciones")
        instituciones_raw = cursor.fetchall()
    except:
        instituciones_raw = []

    instituciones = []
    for inst in instituciones_raw:
        try:
            cursor.execute("SELECT COUNT(*) FROM pacientes WHERE institucion=?", (inst[0],))
            total = cursor.fetchone()[0] if cursor.fetchone() else 0
        except:
            total = 0
        instituciones.append({
            "id": inst[0],
            "nombre": inst[1],
            "estado": inst[2],
            "total": total
        })

    # Cargar usuarios
    try:
        cursor.execute("SELECT usuario, rol, institucion, activo FROM usuarios")
        usuarios_raw = cursor.fetchall()
    except:
        usuarios_raw = []

    usuarios = []
    for u in usuarios_raw:
        usuarios.append({
            "usuario": u[0],
            "rol": u[1],
            "institucion": u[2],
            "activo": u[3]
        })

    # Cargar pacientes
    try:
        cursor.execute("SELECT id, nombre, apellido, dni, institucion, telefono, email FROM pacientes")
        pacientes = cursor.fetchall()
    except:
        pacientes = []

    conn.close()

    return templates.TemplateResponse("admin-pacientes.html", {
        "request": request,
        "instituciones": instituciones,
        "usuarios": usuarios,
        "pacientes": pacientes
    })

# ---------------- Activar / Desactivar usuario ----------------
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

# ---------------- Agregar nuevo usuario ----------------
@router.post("/admin/usuario/agregar")
async def agregar_usuario(usuario: str = Form(...), contrasena: str = Form(...), rol: str = Form(...), institucion: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (usuario, contrasena, rol, institucion, activo) VALUES (?, ?, ?, ?, 1)",
                   (usuario, contrasena, rol, institucion))
    conn.commit()
    conn.close()
    return HTMLResponse(content="<script>window.location.href='/admin/pacientes'</script>")

# ---------------- Agregar nuevo paciente manual ----------------
@router.post("/admin/paciente/manual/agregar")
async def agregar_paciente(
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

# ---------------- Exportar pacientes de una institución ----------------
@router.get("/exportar-pacientes/{institucion_id}")
async def exportar_pacientes(institucion_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pacientes WHERE institucion=?", (institucion_id,))
    pacientes = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.set_auto_page_break(auto=True, margin=10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt=f"Pacientes de la institución: {institucion_id}", ln=True)
    pdf.set_font("Arial", size=10)

    for paciente in pacientes:
        for i, dato in enumerate(paciente):
            linea = f"{columnas[i]}: {dato}"
            pdf.cell(200, 8, txt=linea.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.cell(200, 5, txt="-----------------------------", ln=True)

    conn.close()
    export_path = f"static/doc/pacientes_export_{institucion_id}.pdf"
    pdf.output(export_path)

    return FileResponse(export_path, media_type="application/pdf", filename=f"pacientes_{institucion_id}.pdf")
