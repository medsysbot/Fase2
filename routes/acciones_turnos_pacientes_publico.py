# ╔══════════════════════════════════════════════════════════════════╗
# ║     TURNOS MÉDICOS - FORMULARIO PÚBLICO - BACKEND FASTAPI       ║
# ╚══════════════════════════════════════════════════════════════════╝

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from utils.supabase_helper import supabase, subir_pdf
from utils.email_sender import enviar_email_con_pdf
from utils.pdf_generator import generar_pdf_turno_publico

router = APIRouter()

BUCKET_PDFS = "turnos-pacientes"

# ╔════════════════════════════════════╗
# ║        GUARDAR FORMULARIO         ║
# ╚════════════════════════════════════╝
@router.post("/guardar_turno_publico")
async def guardar_turno_publico(
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    especialidad: str = Form(...),
    profesional: str = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    observaciones: str = Form(...),
    institucion_nombre: str = Form(...)
):
    try:
        inst = (
            supabase.table("instituciones")
            .select("id")
            .eq("nombre", institucion_nombre)
            .single()
            .execute()
        )
        institucion_id = inst.data["id"] if inst.data else None
        if institucion_id is None:
            return JSONResponse(
                {"exito": False, "mensaje": "Clínica no registrada"},
                status_code=404,
            )

        paciente = (
            supabase.table("pacientes")
            .select("id")
            .eq("dni", dni)
            .eq("institucion_id", institucion_id)
            .execute()
        )
        if not paciente.data:
            return JSONResponse(
                {
                    "exito": False,
                    "mensaje": "No pudimos generar su turno. Usted no está registrado en esta institución.",
                },
                status_code=403,
            )

        conflicto = (
            supabase.table("turnos_pacientes")
            .select("id")
            .match(
                {
                    "fecha": fecha,
                    "hora": hora,
                    "profesional": profesional,
                    "institucion_id": institucion_id,
                }
            )
            .execute()
        )
        if conflicto.data:
            return JSONResponse(
                {
                    "exito": False,
                    "mensaje": "El horario seleccionado ya está ocupado. Por favor elija otro turno.",
                },
                status_code=409,
            )

        data = {
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "especialidad": especialidad,
            "profesional": profesional,
            "fecha": fecha,
            "hora": hora,
            "observaciones": observaciones,
            "institucion_id": int(institucion_id),
            "usuario_id": "bot_publico",
        }
        supabase.table("turnos_pacientes").insert(data).execute()
        return {"message": "Turno registrado correctamente"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ╔════════════════════════════════════════════════════════════╗
# ║   GENERAR Y GUARDAR PDF TURNO MÉDICO PÚBLICO (SIN FIRMA)  ║
# ╚════════════════════════════════════════════════════════════╝
@router.post("/generar_pdf_turno_publico")
async def generar_pdf_turno_publico(
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    especialidad: str = Form(...),
    profesional: str = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    observaciones: str = Form(...),
    institucion_nombre: str = Form(...)
):
    try:
        datos = {
            "nombre": f"{nombre} {apellido}",
            "dni": dni,
            "especialidad": especialidad,
            "profesional": profesional,
            "fecha": fecha,
            "hora": hora,
            "observaciones": observaciones,
            "institucion": institucion_nombre,
        }

        pdf_path = generar_pdf_turno_publico(datos)
        nombre_pdf = f"{dni}_turno_publico.pdf"
        with open(pdf_path, "rb") as f:
            pdf_url = subir_pdf(BUCKET_PDFS, nombre_pdf, f)

        (
            supabase.table("turnos_pacientes")
            .update({"pdf_url": pdf_url})
            .eq("dni", dni)
            .eq("fecha", fecha)
            .eq("hora", hora)
            .execute()
        )

        return {"exito": True, "pdf_url": pdf_url}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ╔════════════════════════════════════════════════════════════╗
# ║     ENVIAR PDF TURNO PÚBLICO POR CORREO (PACIENTE)        ║
# ╚════════════════════════════════════════════════════════════╝
@router.post("/enviar_pdf_turno_publico")
async def enviar_pdf_turno_publico(
    nombre: str = Form(...),
    dni: str = Form(...),
    pdf_url: str = Form(...)
):
    try:
        resultado = (
            supabase.table("pacientes")
            .select("email")
            .eq("dni", dni)
            .single()
            .execute()
        )
        email = resultado.data.get("email") if resultado.data else None

        if not email:
            return JSONResponse(
                {"exito": False, "mensaje": "No se encontró un e-mail para este DNI."},
                status_code=404,
            )
        if not pdf_url:
            return JSONResponse(
                {"exito": False, "mensaje": "No se encontró el PDF."},
                status_code=404,
            )

        enviar_email_con_pdf(
            email_destino=email,
            asunto="Turno Médico Confirmado",
            cuerpo=f"Estimado/a {nombre}, adjuntamos el archivo PDF con los datos de su turno.",
            url_pdf=pdf_url,
        )
        return {"exito": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"exito": False, "mensaje": str(e)})
