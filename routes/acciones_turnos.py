# ╔════════════════════════════════════════════════════════════╗
# ║               ACCIONES BACKEND - TURNOS MÉDICOS            ║
# ╚════════════════════════════════════════════════════════════╝
from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from utils.pdf_generator import generar_pdf_turno
from utils.email_sender import enviar_email_con_pdf
from dotenv import load_dotenv
import os
from utils.supabase_helper import supabase, subir_pdf

load_dotenv()
router = APIRouter()

BUCKET_PDFS = "turnos-medicos"

@router.post("/generar_pdf_turno")
async def generar_turno(
    request: Request,
    nombre: str = Form(...),
    dni: str = Form(...),
    especialidad: str = Form(""),
    fecha: str = Form(...),
    horario: str = Form(...),
    profesional: str = Form(""),
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)
        datos = {
            "nombre": nombre,
            "dni": dni,
            "especialidad": especialidad,
            "fecha": fecha,
            "horario": horario,
            "profesional": profesional,
        }
        pdf_path = generar_pdf_turno(datos)
        nombre_pdf = os.path.basename(pdf_path)
        with open(pdf_path, "rb") as f:
            pdf_url = subir_pdf(BUCKET_PDFS, nombre_pdf, f)
        supabase.table("turnos").insert({**datos, "institucion_id": institucion_id, "pdf_url": pdf_url}).execute()
        return JSONResponse({"exito": True, "pdf_url": pdf_url})
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)


@router.post("/enviar_pdf_turno")
async def enviar_pdf_turno(email: str = Form(...), nombre: str = Form(...), dni: str = Form(...)):
    try:
        registros = supabase.table("turnos").select("pdf_url").eq("dni", dni).order("id", desc=True).limit(1).execute()
        pdf_url = registros.data[0]["pdf_url"] if registros.data else None
        if not pdf_url:
            return JSONResponse({"exito": False, "mensaje": "No se encontró el PDF."}, status_code=404)
        enviar_email_con_pdf(
            email_destino=email,
            asunto="Turno Médico",
            cuerpo=f"Estimado/a {nombre}, adjuntamos el turno solicitado.",
            url_pdf=pdf_url,
        )
        return {"exito": True}
    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)

@router.get('/api/especialidades')
async def api_especialidades():
    """Devuelve una lista de especialidades disponibles."""
    return ["Clínica", "Pediatría", "Dermatología"]


@router.get('/api/profesionales')
async def api_profesionales(especialidad: str):
    """Profesionales por especialidad (datos de ejemplo)."""
    mapa = {
        "Clínica": ["Dr. Gómez", "Dra. Pérez"],
        "Pediatría": ["Dr. López"],
        "Dermatología": ["Dra. Martínez"]
    }
    return mapa.get(especialidad, [])


@router.get('/api/horarios')
async def api_horarios(profesional: str, fecha: str):
    """Horarios disponibles (ejemplo)."""
    return ["08:00", "09:00", "10:00"]


@router.post('/solicitar_turno')
async def solicitar_turno_publico(
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    especialidad: str = Form(...),
    profesional: str = Form(...),
    fecha: str = Form(...),
    horario: str = Form(...),
):
    """Registra un turno público y envía confirmación por email."""
    try:
        consulta = (
            supabase.table('pacientes')
            .select('email')
            .eq('dni', dni)
            .single()
            .execute()
        )
        email = consulta.data.get('email') if consulta.data else None
        if not email:
            mensaje = (
                'Lo sentimos, no encontramos su registro como paciente en MEDSYS. '
                'Por favor, acérquese a la clínica para registrarse.'
            )
            return JSONResponse({'exito': False, 'mensaje': mensaje}, status_code=404)

        supabase.table('turnos_medicos').insert({
            'dni': dni,
            'nombre': nombre,
            'apellido': apellido,
            'especialidad': especialidad,
            'fecha': fecha,
            'horario': horario,
            'profesional': profesional,
            'institucion_id': None,
        }).execute()

        from utils.email_sender import enviar_email_simple

        cuerpo = (
            f'Hola {nombre} {apellido},\n\n'
            f'Su turno fue reservado para el {fecha} a las {horario} con '
            f'{profesional} ({especialidad}).\n\n'
            'Dirección de la clínica: ...\n\nSaludos, Equipo MEDSYS'
        )
        enviar_email_simple(email, 'Confirmación de turno', cuerpo)
        return {"exito": True}

    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)
