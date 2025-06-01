# ╔════════════════════════════════════════════════════════════╗
# ║            ACCIONES BACKEND - BÚSQUEDA DE PACIENTES        ║
# ╚════════════════════════════════════════════════════════════╝
from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from utils.supabase_helper import supabase

load_dotenv()
router = APIRouter()

@router.post("/buscar_paciente")
async def buscar_paciente(request: Request, dni: str = Form(...)):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)
        resultado = (
            supabase.table("pacientes")
            .select("nombres, apellido, email, telefono")
            .eq("dni", dni)
            .single()
            .execute()
        )
        if not resultado.data:
            return JSONResponse({"exito": False, "mensaje": "Paciente no encontrado"}, status_code=404)
        datos = {
            "dni": dni,
            "nombres": resultado.data.get("nombres", ""),
            "apellido": resultado.data.get("apellido", ""),
            "email": resultado.data.get("email", ""),
            "telefono": resultado.data.get("telefono", ""),
        }

        supabase.table("busqueda_pacientes").insert({**datos, "institucion_id": institucion_id}).execute()

        return JSONResponse({"exito": True, "datos": datos})
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
