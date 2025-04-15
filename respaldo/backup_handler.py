import os
import json
import sqlite3
from datetime import datetime

# Ruta de backups (ajustar si estás fuera de entorno local)
RUTA_BACKUP = "respaldo/backups"

# Asegura que exista la carpeta
os.makedirs(RUTA_BACKUP, exist_ok=True)

# Ruta de la base de datos
DB_PATH = "static/doc/medsys.db"

def guardar_respaldo_completo(dni_paciente, eliminado_por):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Buscar paciente
    cursor.execute("SELECT * FROM pacientes WHERE dni=?", (dni_paciente,))
    paciente = cursor.fetchone()

    if not paciente:
        conn.close()
        return False

    paciente_dict = {
        "id": paciente[0],
        "nombre": paciente[1],
        "dni": paciente[2],
        "fecha_nacimiento": paciente[3],
        "telefono": paciente[4],
        "direccion": paciente[5],
        "institucion": paciente[6],
        "fecha_eliminacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "eliminado_por": eliminado_por
    }

    # Recolectar datos clínicos relacionados
    def fetch_related_data(tabla, campo="paciente_id"):
        cursor.execute(f"SELECT * FROM {tabla} WHERE {campo}=?", (paciente[0],))
        columnas = [description[0] for description in cursor.description]
        return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]

    paciente_dict["recetas"] = fetch_related_data("recetas")
    paciente_dict["indicaciones"] = fetch_related_data("indicaciones")
    paciente_dict["estudios"] = fetch_related_data("estudios")
    paciente_dict["historia_clinica"] = fetch_related_data("historia_clinica")
    paciente_dict["turnos"] = fetch_related_data("turnos")

    # Guardar respaldo en archivo JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"paciente_{dni_paciente}_{timestamp}.json"
    ruta_archivo = os.path.join(RUTA_BACKUP, nombre_archivo)

    with open(ruta_archivo, "w", encoding="utf-8") as f:
        json.dump(paciente_dict, f, ensure_ascii=False, indent=4)

    conn.close()
    return True
