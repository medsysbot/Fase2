from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
import sqlite3
from respaldo.backup_handler import guardar_respaldo_completo

router = APIRouter()

DB_PATH = "static/doc/medsys.db"

@router.post("/eliminar-paciente")
async def eliminar_paciente(dni: str = Form(...), usuario: str = Form(...)):
    # Guardar respaldo antes de eliminar
    respaldo_exitoso = guardar_respaldo_completo(dni_paciente=dni, eliminado_por=usuario)

    if respaldo_exitoso:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Eliminar datos relacionados
        cursor.execute("DELETE FROM recetas WHERE paciente_id = (SELECT id FROM pacientes WHERE dni=?)", (dni,))
        cursor.execute("DELETE FROM indicaciones WHERE paciente_id = (SELECT id FROM pacientes WHERE dni=?)", (dni,))
        cursor.execute("DELETE FROM estudios WHERE paciente_id = (SELECT id FROM pacientes WHERE dni=?)", (dni,))
        cursor.execute("DELETE FROM historia_clinica WHERE paciente_id = (SELECT id FROM pacientes WHERE dni=?)", (dni,))
        cursor.execute("DELETE FROM turnos WHERE paciente_id = (SELECT id FROM pacientes WHERE dni=?)", (dni,))
        
        # Finalmente, eliminar paciente
        cursor.execute("DELETE FROM pacientes WHERE dni=?", (dni,))
        
        conn.commit()
        conn.close()
        return RedirectResponse(url="/registro", status_code=303)
    else:
        return {"error": "Paciente no encontrado o respaldo fallido"}
