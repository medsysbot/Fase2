from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from utils.supabase_helper import supabase, subir_pdf
from utils.pdf_generator import generar_pdf_busqueda
import os
import tempfile

router = APIRouter()

BUCKET = "busqueda-pacientes"

def tiene_datos(res):
    # Devuelve True si la consulta devuelve una lista con al menos un registro, False si no o si falla
    try:
        return bool(res.data and len(res.data) > 0)
    except Exception:
        return False

@router.post("/api/buscar_paciente")
async def buscar_paciente(request: Request):
    body = await request.json()
    dni = body.get("dni")

    hc_completa = supabase.table("historia_clinica_completa").select("*").eq("dni", dni).execute()
    hc_resumida = supabase.table("historia_clinica_resumida").select("*").eq("dni", dni).execute()
    consulta_diaria = supabase.table("consulta_diaria").select("*").eq("dni", dni).execute()
    recetas = supabase.table("recetas_medicas").select("*").eq("dni", dni).execute()
    turnos = supabase.table("turnos_pacientes").select("*").eq("dni", dni).execute()
    estudios = supabase.table("estudios").select("*").eq("dni", dni).execute()
    busqueda = supabase.table("busqueda_pacientes").select("pdf_url").eq("dni", dni).execute()

    result = {
        "historia_clinica_completa": tiene_datos(hc_completa),
        "historia_clinica_resumida": tiene_datos(hc_resumida),
        "consulta_diaria": tiene_datos(consulta_diaria),
        "recetas": tiene_datos(recetas),
        "turnos": tiene_datos(turnos),
        "estudios": tiene_datos(estudios),
        "pdf_url": busqueda.data[0]["pdf_url"] if busqueda.data else None,
    }
    return JSONResponse(result)


@router.post("/api/guardar_paciente")
async def guardar_paciente(request: Request):
    body = await request.json()
    dni = body.get("dni")
    try:
        datos = {
            "paciente": supabase.table("registro_pacientes")
            .select("*")
            .eq("dni", dni)
            .single()
            .execute()
            .data,
            "historia_clinica_completa": supabase.table(
                "historia_clinica_completa"
            )
            .select("*")
            .eq("dni", dni)
            .execute()
            .data,
            "historia_clinica_resumida": supabase.table(
                "historia_clinica_resumida"
            )
            .select("*")
            .eq("dni", dni)
            .execute()
            .data,
            "consultas": supabase.table("consulta_diaria")
            .select("*")
            .eq("dni", dni)
            .execute()
            .data,
            "recetas": supabase.table("recetas_medicas")
            .select("*")
            .eq("dni", dni)
            .execute()
            .data,
            "indicaciones": supabase.table("indicaciones_medicas")
            .select("*")
            .eq("dni", dni)
            .execute()
            .data,
            "estudios": supabase.table("estudios")
            .select("*")
            .eq("dni", dni)
            .execute()
            .data,
            "turnos": supabase.table("turnos_pacientes")
            .select("*")
            .eq("dni", dni)
            .execute()
            .data,
        }
        pdf_path = generar_pdf_busqueda(datos)
        nombre_pdf = os.path.basename(pdf_path)
        with open(pdf_path, "rb") as f:
            pdf_url = subir_pdf(BUCKET, nombre_pdf, f)
        supabase.table("busqueda_pacientes").upsert(
            {
                "dni": dni,
                "fecha": datetime.utcnow().isoformat(),
                "pdf_url": pdf_url,
            }
        ).execute()
        return JSONResponse({"ok": True, "pdf_url": pdf_url})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)})


@router.post("/api/borrar_paciente")
async def borrar_paciente(request: Request):
    body = await request.json()
    dni = body.get("dni")
    try:
        tablas = [
            "historia_clinica_completa",
            "historia_clinica_resumida",
            "consulta_diaria",
            "recetas_medicas",
            "turnos_pacientes",
            "estudios",
            "busqueda_pacientes",
        ]
        for tabla in tablas:
            supabase.table(tabla).delete().eq("dni", dni).execute()
        return JSONResponse({"ok": True})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)})
