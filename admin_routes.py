from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from fpdf import FPDF

router = APIRouter()
templates = Jinja2Templates(directory="templates")
DB_PATH = "static/doc/medsys.db"

# ---------------- PANEL ORIGINAL PACIENTES ----------------
@router.get("/admin/pacientes", response_class=HTMLResponse)
async def admin_pacientes(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, nombre, estado FROM instituciones")
    instituciones_raw = cursor.fetchall()
    instituciones = []
    for inst in instituciones_raw:
        cursor.execute("SELECT COUNT(*) FROM pacientes WHERE institucion_id=?", (inst[0],))
        total = cursor.fetchone()[0]
        instituciones.append({
            "id": inst[0],
            "nombre": inst[1],
            "estado": inst[2],
            "total": total
        })

    cursor.execute("SELECT usuario, nombres, apellido, rol, institucion_id, activo FROM usuarios")
    usuarios_raw = cursor.fetchall()
    usuarios = []
    for u in usuarios_raw:
        usuarios.append({
            "usuario": u[0],
            "nombres": u[1],
            "apellido": u[2],
            "rol": u[3],
            "institucion": u[4],
            "activo": u[5]
        })

    conn.close()
    return templates.TemplateResponse("admin-pacientes.html", {
        "request": request,
        "instituciones": instituciones,
        "usuarios": usuarios
    })

# ---------------- PANEL NUEVO: CONTROL TOTAL ----------------
@router.get("/admin/control-total", response_class=HTMLResponse)
async def control_total(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, nombre, estado FROM instituciones")
    instituciones_raw = cursor.fetchall()
    instituciones = []
    for inst in instituciones_raw:
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE institucion_id=?", (inst[0],))
        total_usuarios = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pacientes WHERE institucion_id=?", (inst[0],))
        total_pacientes = cursor.fetchone()[0]
        instituciones.append({
            "id": inst[0],
            "nombre": inst[1],
            "estado": inst[2],
            "total_usuarios": total_usuarios,
            "total_pacientes": total_pacientes
        })

    cursor.execute("SELECT usuario, nombres, apellido, rol, institucion_id, activo FROM usuarios")
    usuarios_raw = cursor.fetchall()
    usuarios = []
    for u in usuarios_raw:
        usuarios.append({
            "usuario": u[0],
            "nombres": u[1],
            "apellido": u[2],
            "rol": u[3],
            "institucion": u[4],
            "activo": u[5]
        })

    conn.close()
    return templates.TemplateResponse("control-total.html", {
        "request": request,
        "instituciones": instituciones,
        "usuarios": usuarios
    })

# ---------------- PANEL NUEVO: SOLO INSTITUCIONES ----------------
@router.get("/admin/instituciones", response_class=HTMLResponse)
async def admin_instituciones(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, nombre, estado FROM instituciones")
    instituciones_raw = cursor.fetchall()
    instituciones = []
    for inst in instituciones_raw:
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE institucion_id=?", (inst[0],))
        total_usuarios = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pacientes WHERE institucion_id=?", (inst[0],))
        total_pacientes = cursor.fetchone()[0]
        instituciones.append({
            "id": inst[0],
            "nombre": inst[1],
            "estado": inst[2],
            "total_usuarios": total_usuarios,
            "total_pacientes": total_pacientes
        })

    conn.close()
    return templates.TemplateResponse("admin-instituciones.html", {
        "request": request,
        "instituciones": instituciones
    })

# ---------------- ACCIONES USUARIOS ----------------
@router.post("/admin/usuario/agregar")
async def agregar_usuario(
    usuario: str = Form(...),
    contrasena: str = Form(...),
    nombres: str = Form(...),
    apellido: str = Form(...),
    rol: str = Form(...),
    institucion: str = Form(...)
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO usuarios (usuario, contraseña, nombres, apellido, rol, institucion_id, activo)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    """, (usuario, contrasena, nombres, apellido, rol, institucion))
    conn.commit()
    conn.close()
    return HTMLResponse(content="<script>window.location.href='/admin/pacientes'</script>")

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

@router.post("/admin/usuario/eliminar")
async def eliminar_usuario(usuario: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE usuario=?", (usuario,))
    conn.commit()
    conn.close()
    return HTMLResponse(content="<script>window.location.href='/admin/pacientes'</script>")

# ---------------- EXPORTAR PACIENTES PDF ----------------
@router.get("/exportar-pacientes/{institucion_id}")
async def exportar_pacientes(institucion_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pacientes WHERE institucion_id=?", (institucion_id,))
    pacientes = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt=f"Pacientes de la institución: {institucion_id}", ln=True)
    pdf.set_font("Arial", size=10)

    for p in pacientes:
        for i, dato in enumerate(p):
            linea = f"{columnas[i]}: {dato}"
            pdf.cell(200, 8, txt=linea.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.cell(200, 5, txt="-----------------------------", ln=True)

    conn.close()
    export_path = f"static/doc/pacientes_export_{institucion_id}.pdf"
    pdf.output(export_path)
    return FileResponse(export_path, media_type="application/pdf", filename=f"pacientes_{institucion_id}.pdf")

# ---------------- PAUSAR / ACTIVAR INSTITUCIÓN ----------------
@router.post("/admin/pausar-institucion")
async def pausar_institucion(id: int = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT estado FROM instituciones WHERE id=?", (id,))
    estado_actual = cursor.fetchone()
    if estado_actual:
        nuevo_estado = "pausada" if estado_actual[0] == "activa" else "activa"
        cursor.execute("UPDATE instituciones SET estado=? WHERE id=?", (nuevo_estado, id))
        conn.commit()
    conn.close()
    return HTMLResponse(content="<script>window.location.href='/admin/control-total'</script>")

# ---------------- ELIMINAR INSTITUCIÓN ----------------
@router.post("/admin/eliminar-institucion")
async def eliminar_institucion(id: int = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM instituciones WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return HTMLResponse(content="<script>window.location.href='/admin/control-total'</script>")
