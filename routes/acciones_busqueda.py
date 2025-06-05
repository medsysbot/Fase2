from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from supabase import create_client, Client
import os, json
from datetime import datetime

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.post("/api/buscar_paciente")
async def buscar_paciente(request: Request):
    body = await request.json()
    dni = body.get("dni")

    busqueda = supabase.table("busqueda_pacientes").select("*").eq("dni", dni).execute()

    hc_completa = supabase.table("historia_clinica_completa").select("id").eq("dni", dni).execute()
    hc_resumida = supabase.table("historia_clinica_resumida").select("id").eq("dni", dni).execute()
    consulta_diaria = supabase.table("consulta_diaria").select("id").eq("dni", dni).execute()
    recetas = supabase.table("recetas").select("id").eq("dni", dni).execute()
    turnos = supabase.table("turnos_pacientes").select("id").eq("dni", dni).execute()
    estudios = supabase.table("estudios_medicos").select("id").eq("dni", dni).execute()

    result = {
        "historia_clinica_completa": bool(hc_completa.data),
        "historia_clinica_resumida": bool(hc_resumida.data),
        "consulta_diaria": bool(consulta_diaria.data),
        "recetas": bool(recetas.data),
        "turnos": bool(turnos.data),
        "estudios": bool(estudios.data),
        "pdf_url": None
    }
    if any(result.values()):
        result["pdf_url"] = f"https://{SUPABASE_URL}/storage/v1/object/public/busqueda-pacientes/{dni}.pdf"
    return JSONResponse(result)

@router.post("/api/enviar_pdf_paciente")
async def enviar_pdf_paciente(request: Request):
    body = await request.json()
    dni = body.get("dni")
    email = body.get("email")
    pdf_url = f"https://{SUPABASE_URL}/storage/v1/object/public/busqueda-pacientes/{dni}.pdf"
    try:
        return JSONResponse({"ok": True})
    except Exception as e:
        return JSONResponse({"ok": False})

@router.post("/api/borrar_paciente")
async def borrar_paciente(request: Request):
    body = await request.json()
    dni = body.get("dni")
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    tablas = [
        "historia_clinica_completa",
        "historia_clinica_resumida",
        "consulta_diaria",
        "recetas",
        "turnos_pacientes",
        "estudios_medicos",
        "busqueda_pacientes"
    ]
    backup_data = {}
    for tabla in tablas:
        res = supabase.table(tabla).select("*").eq("dni", dni).execute()
        backup_data[tabla] = res.data
    backup_json = json.dumps(backup_data, default=str)
    backup_path = f"busqueda-pacientes/{dni}-{timestamp}.json"
    try:
        supabase.storage().from_("busqueda-pacientes").upload(backup_path, backup_json)
    except Exception as e:
        return JSONResponse({"ok": False, "error": "No se pudo guardar el backup."})
    try:
        for tabla in tablas:
            supabase.table(tabla).delete().eq("dni", dni).execute()
        return JSONResponse({"ok": True})
    except Exception as e:
        return JSONResponse({"ok": False, "error": "No se pudo eliminar el paciente de todas las tablas."})
