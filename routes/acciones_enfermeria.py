
# ╔════════════════════════════════════════════════════════════╗
# ║         ACCIONES BACKEND - DATOS DE ENFERMERÍA            ║
# ╚════════════════════════════════════════════════════════════╝

from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from utils.supabase_helper import supabase
from datetime import datetime

router = APIRouter()

@router.post("/guardar_datos_enfermeria")
async def guardar_datos_enfermeria(
    request: Request,
    dni: str = Form(...),
    institucion_id: str = Form(...),
    usuario_id: str = Form(...),
    profesional: str = Form(...),
    motivo_consulta: str = Form(...),
    hora: str = Form(...),
    temperatura: float = Form(...),
    saturacion: float = Form(...),
    ta: float = Form(...),
    tad: float = Form(...),
    frecuencia_cardiaca: float = Form(...),
    glasgow: int = Form(...),
    dolor: int = Form(...),
    glucemia: float = Form(...),
    triaje: str = Form(...)
):
    try:
        supabase.table("datos_enfermeria").insert({
            "dni": dni,
            "institucion_id": institucion_id,
            "usuario_id": usuario_id,
            "profesional": profesional,
            "motivo_consulta": motivo_consulta,
            "hora": hora,
            "temperatura": temperatura,
            "saturacion": saturacion,
            "ta": ta,
            "tad": tad,
            "frecuencia_cardiaca": frecuencia_cardiaca,
            "glasgow": glasgow,
            "dolor": dolor,
            "glucemia": glucemia,
            "triaje": triaje
        }).execute()
        return JSONResponse({"exito": True, "mensaje": "Datos de enfermería guardados correctamente"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
