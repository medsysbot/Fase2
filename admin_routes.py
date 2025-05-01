from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from fpdf import FPDF

router = APIRouter()
templates = Jinja2Templates(directory="templates")
DB_PATH = "static/doc/medsys.db"

# PANEL DE CONTROL TOTAL
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

# INSTITUCIONES
@router.post("/admin/institucion/agregar")
async def agregar_institucion(nombre: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO instituciones (nombre, estado) VALUES (?, 'activa')", (nombre,))
    conn.commit()
    conn.close()
    return HTMLResponse("<script>location.href='/admin/control-total'</script>")

@router.post("/admin/institucion/editar")
async def editar_institucion(id: int = Form(...), nombre: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE instituciones SET nombre=? WHERE id=?", (nombre, id))
    conn.commit()
    conn.close()
    return HTMLResponse("<script>location.href='/admin/control-total'</script>")

@router.post("/admin/institucion/pausar-activar")
async def pausar_activar_institucion(id: int = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT estado FROM instituciones WHERE id=?", (id,))
    estado = cursor.fetchone()[0]
    nuevo = "pausada" if estado == "activa" else "activa"
    cursor.execute("UPDATE instituciones SET estado=? WHERE id=?", (nuevo, id))
    conn.commit()
    conn.close()
    return HTMLResponse("<script>location.href='/admin/control-total'</script>")

@router.post("/admin/institucion/eliminar")
async def eliminar_institucion(id: int = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM instituciones WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return HTMLResponse("<script>location.href='/admin/control-total'</script>")

# USUARIOS
@router.post("/admin/usuario/agregar")
async def agregar_usuario(usuario: str = Form(...), contrasena: str = Form(...),
                          nombres: str = Form(...), apellido: str = Form(...),
                          rol: str = Form(...), institucion: int = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO usuarios (usuario, contrasena, nombres, apellido, rol, institucion_id, activo)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    """, (usuario, contrasena, nombres, apellido, rol, institucion))
    conn.commit()
    conn.close()
    return HTMLResponse("<script>location.href='/admin/control-total'</script>")

@router.post("/admin/usuario/editar")
async def editar_usuario(usuario: str = Form(...), nombres: str = Form(...),
                         apellido: str = Form(...), rol: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET nombres=?, apellido=?, rol=? WHERE usuario=?",
                   (nombres, apellido, rol, usuario))
    conn.commit()
    conn.close()
    return HTMLResponse("<script>location.href='/admin/control-total'</script>")

@router.post("/admin/usuario/pausar-activar")
async def pausar_activar_usuario(usuario: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT activo FROM usuarios WHERE usuario=?", (usuario,))
    actual = cursor.fetchone()[0]
    nuevo = 0 if actual == 1 else 1
    cursor.execute("UPDATE usuarios SET activo=? WHERE usuario=?", (nuevo, usuario))
    conn.commit()
    conn.close()
    return HTMLResponse("<script>location.href='/admin/control-total'</script>")

@router.post("/admin/usuario/eliminar")
async def eliminar_usuario(usuario: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE usuario=?", (usuario,))
    conn.commit()
    conn.close()
    return HTMLResponse("<script>location.href='/admin/control-total'</script>")

# PACIENTES
@router.post("/admin/paciente/eliminar")
async def eliminar_paciente_total(dni: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM pacientes WHERE dni=?", (dni,))
    paciente = cursor.fetchone()
    if not paciente:
        conn.close()
        return HTMLResponse("<script>alert('Paciente no encontrado.'); location.href='/admin/control-total'</script>")
    pid = paciente[0]
    for tabla in ["recetas", "indicaciones", "estudios", "historia_clinica", "turnos"]:
        cursor.execute(f"DELETE FROM {tabla} WHERE paciente_id=?", (pid,))
    cursor.execute("DELETE FROM pacientes WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    return HTMLResponse("<script>alert('Paciente eliminado.'); location.href='/admin/control-total'</script>")

@router.get("/admin/paciente/exportar/{dni}")
async def exportar_paciente(dni: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes WHERE dni=?", (dni,))
    datos = cursor.fetchone()
    columnas = [desc[0] for desc in cursor.description]
    if not datos:
        return HTMLResponse("<script>alert('Paciente no encontrado.'); location.href='/admin/control-total'</script>")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Datos Completos del Paciente", ln=True)
    pdf.set_font("Arial", "", 12)
    for i in range(len(columnas)):
        pdf.cell(0, 8, f"{columnas[i]}: {datos[i]}", ln=True)
    export_path = f"static/doc/paciente_{dni}_completo.pdf"
    pdf.output(export_path)
    conn.close()
    return FileResponse(export_path, media_type="application/pdf", filename=f"paciente_{dni}.pdf")

# FICHA PACIENTE MANUAL
@router.get("/admin/ficha-paciente", response_class=HTMLResponse)
async def ficha_paciente_get(request: Request):
    return templates.TemplateResponse("ficha-paciente.html", {"request": request})

@router.post("/admin/ficha-paciente/eliminar")
async def eliminar_paciente_ficha(dni: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM pacientes WHERE dni=?", (dni,))
    paciente = cursor.fetchone()
    if not paciente:
        conn.close()
        return HTMLResponse("<script>alert('Paciente no encontrado.'); location.href='/admin/ficha-paciente'</script>")
    pid = paciente[0]
    for tabla in ["recetas", "indicaciones", "estudios", "historia_clinica", "turnos"]:
        cursor.execute(f"DELETE FROM {tabla} WHERE paciente_id=?", (pid,))
    cursor.execute("DELETE FROM pacientes WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    return HTMLResponse("<script>alert('Paciente eliminado correctamente.'); location.href='/admin/ficha-paciente'</script>")

@router.post("/admin/ficha-paciente/exportar")
async def exportar_paciente_ficha(dni: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes WHERE dni=?", (dni,))
    datos = cursor.fetchone()
    columnas = [desc[0] for desc in cursor.description]
    if not datos:
        return HTMLResponse("<script>alert('Paciente no encontrado.'); location.href='/admin/ficha-paciente'</script>")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Ficha Completa del Paciente", ln=True)
    pdf.set_font("Arial", "", 12)
    for i in range(len(columnas)):
        pdf.cell(0, 8, f"{columnas[i]}: {datos[i]}", ln=True)
    export_path = f"static/doc/paciente_{dni}_completo.pdf"
    pdf.output(export_path)
    conn.close()
    return FileResponse(export_path, media_type="application/pdf", filename=f"paciente_{dni}.pdf")

# VER PACIENTE EN PANTALLA (HTML)
@router.post("/admin/ficha-paciente/ver", response_class=HTMLResponse)
async def ver_paciente_ficha(request: Request, dni: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes WHERE dni=?", (dni,))
    datos = cursor.fetchone()
    columnas = [desc[0] for desc in cursor.description]
    conn.close()

    if not datos:
        return HTMLResponse("<script>alert('Paciente no encontrado.'); location.href='/admin/ficha-paciente'</script>")

    return templates.TemplateResponse("ver-paciente.html", {
        "request": request,
        "columnas": columnas,
        "datos": datos
    })
