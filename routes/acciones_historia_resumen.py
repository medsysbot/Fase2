from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/generar_pdf_historia_resumen")
async def generar_pdf_historia_resumen(
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    edad: str = Form(...),
    motivo: str = Form(...),
    diagnostico: str = Form(...),  # ← Corrección aquí
    tratamiento: str = Form(...),
    observaciones: str = Form(...),
    institucion_id: str = Form(None),
):
    try:
        # Aquí toda la lógica que ya tenías para guardar en Supabase,
        # generar el PDF, etc., usando 'diagnostico' y no 'diagnostostico'
        # Por ejemplo:
        # guardar_en_supabase(dni, nombre, apellido, edad, motivo, diagnostico, tratamiento, observaciones, institucion_id)
        # pdf_url = generar_pdf_historia_resumida(...)

        return JSONResponse({"exito": True, "mensaje": "Historia resumida guardada correctamente"})
    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)}, status_code=400)
