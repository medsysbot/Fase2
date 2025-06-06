# ╔════════════════════════════════════════════════════╗
# ║     CONSULTA DIARIA - ENDPOINTS BACKEND FASTAPI   ║
# ╚════════════════════════════════════════════════════╝

from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from utils.supabase_helper import supabase, subir_pdf, SUPABASE_URL
from utils.email_sender import enviar_email_con_pdf
from utils.pdf_generator import generar_pdf_consulta_diaria
from utils.image_utils import descargar_imagen, guardar_imagen_temporal
import os
import logging

router = APIRouter()

BUCKET_PDFS = "consulta-diaria"
BUCKET_FIRMAS = "firma-sello-usuarios"
TABLE_NAME = "consulta_diaria"

# ╔════════════════════════════════════╗
# ║        GUARDAR FORMULARIO         ║
# ╚════════════════════════════════════╝
@router.post("/guardar_consulta_diaria")
async def guardar_consulta_diaria(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    fecha: str = Form(...),
    diagnostico: str = Form(...),
    evolucion: str = Form(...),
    indicaciones: str = Form(...),
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

        data = {
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "evolucion": evolucion,
            "indicaciones": indicaciones,
            "institucion_id": int(institucion_id),
            "usuario_id": usuario,
        }
        supabase.table(TABLE_NAME).insert(data).execute()
        return {"message": "Guardado exitosamente"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        logging.error(f"Error al guardar consulta diaria: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# ╔════════════════════════════════════════════╗
# ║     GENERAR Y SUBIR PDF DE LA CONSULTA     ║
# ╚════════════════════════════════════════════╝

@router.post("/generar_pdf_consulta_diaria")
async def generar_pdf_consulta_diaria_route(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    fecha: str = Form(...),
    diagnostico: str = Form(...),
    evolucion: str = Form(...),
    indicaciones: str = Form(...),
):
    try:
        usuario = request.session.get("usuario")
        institucion_session = request.session.get("institucion_id")
        if not usuario or institucion_session is None:
            return JSONResponse({"error": "Falta sesión de usuario."}, status_code=403)

        usuario_id = str(usuario)
        institucion_id = str(institucion_session)

        campos = {
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "evolucion": evolucion,
            "indicaciones": indicaciones,
            "institucion_id": institucion_id,
            "usuario_id": usuario_id,
        }
        print("VALORES RECIBIDOS:", campos)
        faltantes = [c for c, v in campos.items() if not str(v).strip()]
        if faltantes:
            return JSONResponse(
                status_code=422,
                content={"error": f"Faltan campos obligatorios: {', '.join(faltantes)}"},
            )

        datos = {
            "paciente": f"{nombre} {apellido}".strip(),
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "evolucion": evolucion,
            "indicaciones": indicaciones,
        }

        base_firma = f"firma_{usuario_id}_{institucion_id}"
        base_sello = f"sello_{usuario_id}_{institucion_id}"
        contenido_firma, nombre_firma = descargar_imagen(
            supabase, BUCKET_FIRMAS, base_firma
        )
        contenido_sello, nombre_sello = descargar_imagen(
            supabase, BUCKET_FIRMAS, base_sello
        )

        firma_path = guardar_imagen_temporal(contenido_firma, nombre_firma) if contenido_firma else None
        sello_path = guardar_imagen_temporal(contenido_sello, nombre_sello) if contenido_sello else None

        if nombre_firma:
            datos["firma_url"] = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_FIRMAS}/{nombre_firma}"
        if nombre_sello:
            datos["sello_url"] = (
                f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_FIRMAS}/{nombre_sello}"
            )

        try:
            pdf_path = generar_pdf_consulta_diaria(datos, firma_path, sello_path)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)

        nombre_pdf = os.path.basename(pdf_path)
        try:
            with open(pdf_path, "rb") as f:
                pdf_url = subir_pdf(BUCKET_PDFS, nombre_pdf, f)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)

        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)

        supabase.table(TABLE_NAME).insert({
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "fecha": fecha,
            "diagnostico": diagnostico,
            "evolucion": evolucion,
            "indicaciones": indicaciones,
            "institucion_id": institucion_id,
            "usuario_id": usuario_id,
            "pdf_url": pdf_url,
        }).execute()

        return {"pdf_url": pdf_url}
    except Exception as e:
        import traceback
        traceback.print_exc()
        logging.error(f"Error al generar PDF de consulta diaria: {e}")
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)

# ╔════════════════════════════════════════════════╗
# ║     ENVIAR CONSULTA DIARIA POR CORREO EMAIL    ║
# ╚════════════════════════════════════════════════╝
@router.post("/enviar_pdf_consulta_diaria")
async def enviar_pdf_consulta_diaria(
    dni: str = Form(...),
    pdf_url: str = Form(...),
    nombre: str = Form(None)
):
    try:
        paciente = supabase.table("registro_pacientes").select("email").eq("dni", dni).single().execute()
        email = paciente.data.get("email") if paciente.data else None

        if not email:
            return JSONResponse(status_code=404, content={"error": "Email no encontrado"})

        asunto = "Consulta Diaria - PDF"
        mensaje = "Adjuntamos el archivo correspondiente a la consulta diaria realizada."
        if nombre:
            mensaje = f"Estimado/a {nombre}, adjuntamos la consulta diaria."
        enviar_email_con_pdf(email, asunto, mensaje, pdf_url)
        return {"message": "Correo enviado correctamente"}

    except Exception as e:
        import traceback
        traceback.print_exc()
        logging.error(f"Error al enviar correo: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
