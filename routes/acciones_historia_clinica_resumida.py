from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
import os
import datetime

from utils.pdf_generator import generar_pdf_resumen

# Asume que estos helpers y la instancia supabase ya están importados
# from .helpers import descargar_imagen, guardar_imagen_temporal, generar_pdf_resumen, subir_pdf, enviar_email_con_pdf
# from .db import supabase

router = APIRouter()

BUCKET_FIRMAS = "firma-sello-usuarios"
BUCKET = "historia-resumen"  # Nombre del bucket para los PDF de historia clínica resumida

@router.post("/generar_pdf_historia_resumen")
async def generar_pdf_historia_resumen(
    request: Request,
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
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)
        paciente = f"{nombre} {apellido}"

        datos = {
            "paciente": paciente,
            "dni": dni,
            "edad": edad,
            "motivo": motivo,
            "diagnostico": diagnostico,
            "tratamiento": tratamiento,
            "observaciones": observaciones
        }

        # Firma y sello temporales
        firma_path = sello_path = None
        base_firma = f"firma_{usuario}_{institucion_id}"
        base_sello = f"sello_{usuario}_{institucion_id}"
        contenido_firma, nombre_firma = descargar_imagen(
            supabase, BUCKET_FIRMAS, base_firma
        )
        contenido_sello, nombre_sello = descargar_imagen(
            supabase, BUCKET_FIRMAS, base_sello
        )

        if contenido_firma:
            firma_path = guardar_imagen_temporal(contenido_firma, nombre_firma)

        if contenido_sello:
            sello_path = guardar_imagen_temporal(contenido_sello, nombre_sello)

        # Generar PDF
        pdf_path = generar_pdf_resumen(datos, firma_path, sello_path)

        # Subir a Supabase
        nombre_archivo = f"{dni}_resumen_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        with open(pdf_path, "rb") as f:
            pdf_url = subir_pdf(BUCKET, nombre_archivo, f)

        # Eliminar PDF local
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        # Eliminar archivos temporales de firma y sello
        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)

        # Guardar en Supabase DB
        supabase.table("historia_clinica_resumida").insert({
            "paciente": paciente,
            "dni": dni,
            "edad": edad,
            "motivo": motivo,
            "diagnostico": diagnostico,
            "tratamiento": tratamiento,
            "observaciones": observaciones,
            "pdf_url": pdf_url,
            "institucion_id": institucion_id,
        }).execute()

        return JSONResponse({"exito": True, "pdf_url": pdf_url})

    except Exception as e:
        return JSONResponse(content={"exito": False, "mensaje": str(e)}, status_code=500)

# ╔════════════════════════════════════════════════════════════╗
# ║        RUTA: ENVIAR HISTORIA CLÍNICA POR CORREO           ║
# ╚════════════════════════════════════════════════════════════╝

@router.post("/enviar_pdf_historia_resumen")
async def enviar_historia_resumen(
    email: str = Form(...),
    paciente: str = Form(...),
    pdf_url: str = Form(...),
):
    try:
        if not pdf_url:
            return JSONResponse(
                content={"exito": False, "mensaje": "No se encontró el PDF."},
                status_code=404,
            )

        enviar_email_con_pdf(
            email_destino=email,
            asunto="Historia Clínica Resumida",
            cuerpo=f"Estimado/a {paciente}, adjuntamos su historia clínica.",
            url_pdf=pdf_url,
        )

        return JSONResponse({"exito": True, "mensaje": "Historia clínica enviada correctamente"})

    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)}, status_code=400)
