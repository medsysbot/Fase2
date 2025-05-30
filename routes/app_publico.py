# ╔══════════════════════════════════════════════════════════╗
# ║        ENDPOINTS PORTAL PÚBLICO - MEDSYS                ║
# ║  Todas las rutas públicas (turnos, info, landing, etc.) ║
# ╚══════════════════════════════════════════════════════════╝

from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from supabase import create_client, Client
from utils.email_sender import enviar_email_simple

import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Instanciar cliente de Supabase (ajusta tus variables)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ╔══════════════════════════════════════════════════════════╗
# ║   Splash público (opcional, podés quitar si no usás)    ║
# ╚══════════════════════════════════════════════════════════╝
@router.get("/splash-turno", response_class=HTMLResponse)
async def splash_turno(request: Request):
    return templates.TemplateResponse("app_publico/splash_turno_publico.html", {"request": request})

# ╔══════════════════════════════════════════════════════════╗
# ║  Formulario público para solicitar turnos médicos       ║
# ╚══════════════════════════════════════════════════════════╝
@router.get("/turnos-publico", response_class=HTMLResponse)
async def turno_publico(request: Request):
    return templates.TemplateResponse("app_publico/formulario_turnos_publico.html", {"request": request})

# ╔══════════════════════════════════════════════════════════╗
# ║      Registro de turno público + email confirmación      ║
# ╚══════════════════════════════════════════════════════════╝
@router.post("/solicitar_turno_publico")
async def solicitar_turno_publico(
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    especialidad: str = Form(...),
    profesional: str = Form(...),
    fecha: str = Form(...),
    horario: str = Form(...),
):
    try:
        # Buscar email en la tabla pacientes
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

        # Guardar el turno en la tabla de turnos
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

        # Enviar email de confirmación
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

# ╔══════════════════════════════════════════════════════════╗
# ║    Espacio para futuras rutas públicas (info, landing)  ║
# ╚══════════════════════════════════════════════════════════╝

# Ejemplo:
# @router.get("/info-publica")
# async def info_publica(request: Request):
#     return templates.TemplateResponse("app_publico/info_publica.html", {"request": request})
