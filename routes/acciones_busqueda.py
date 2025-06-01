# ╔════════════════════════════════════════════════════════════╗
# ║            ACCIONES BACKEND - BÚSQUEDA DE PACIENTES        ║
# ╚════════════════════════════════════════════════════════════╝
from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from utils.supabase_helper import supabase, subir_pdf
from utils.pdf_generator import generar_pdf_busqueda
from utils.email_sender import enviar_email_con_pdf

load_dotenv()
router = APIRouter()
BUCKET_PDFS = "busqueda-de-pacientes"

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

        paciente = resultado.data

        def _datos(tabla):
            res = supabase.table(tabla).select("*").eq("dni", dni).execute()
            return res.data or []

        datos_pdf = {
            "paciente": {**paciente, "dni": dni},
            "historia_clinica_completa": _datos("historia_clinica_completa"),
            "historia_clinica_resumida": _datos("historia_resumen"),
            "consultas": _datos("consultas"),
            "recetas": _datos("recetas_medicas"),
            "indicaciones": _datos("indicaciones_medicas"),
            "estudios": _datos("estudios"),
            "turnos": _datos("turnos_medicos"),
        }

        pdf_path = generar_pdf_busqueda(datos_pdf)
        filename = os.path.basename(pdf_path)
        with open(pdf_path, "rb") as file_data:
            pdf_url = subir_pdf(BUCKET_PDFS, filename, file_data)

        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        supabase.table("busqueda_pacientes").insert({
            "dni": dni,
            "nombres": paciente.get("nombres"),
            "apellido": paciente.get("apellido"),
            "telefono": paciente.get("telefono"),
            "email": paciente.get("email"),
            "usuario_id": usuario,
            "pdf_url": pdf_url,
            "institucion_id": institucion_id,
        }).execute()

        if paciente.get("email"):
            try:
                enviar_email_con_pdf(
                    email_destino=paciente["email"],
                    asunto="Búsqueda de Paciente",
                    cuerpo=(
                        f"Estimado/a {paciente.get('nombres','')} {paciente.get('apellido','')},\n"
                        "Adjuntamos el resumen de su información médica."),
                    url_pdf=pdf_url,
                )
            except Exception:
                pass

        return JSONResponse({"exito": True, "datos": paciente, "pdf_url": pdf_url})
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)


@router.post("/enviar_pdf_busqueda")
async def enviar_pdf_busqueda(dni: str = Form(...), pdf_url: str = Form(...)):
    """Envía el PDF generado al email del paciente."""
    try:
        resultado = supabase.table("pacientes").select("nombres, apellido, email").eq("dni", dni).single().execute()
        datos = resultado.data
        if not datos or not datos.get("email"):
            return JSONResponse({"exito": False, "mensaje": "No se encontró un e-mail para este DNI."}, status_code=404)
        if not pdf_url:
            return JSONResponse(content={"exito": False, "mensaje": "No se encontró el PDF."}, status_code=404)

        enviar_email_con_pdf(
            email_destino=datos["email"],
            asunto="Búsqueda de Paciente",
            cuerpo=f"Estimado/a {datos.get('nombres','')} {datos.get('apellido','')}, adjuntamos su información.",
            url_pdf=pdf_url,
        )
        return {"exito": True}
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
