from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
import sqlite3

router = APIRouter()
DB_PATH = "static/doc/medsys.db"

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
