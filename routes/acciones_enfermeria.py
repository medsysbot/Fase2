# ╔════════════════════════════════════════════════════════════╗
# ║            ACCIONES BACKEND - ENFERMERÍA                  ║
# ╚════════════════════════════════════════════════════════════╝
from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from utils import generar_pdf_enfermeria, enviar_email_con_pdf
from utils.supabase_helper import supabase, subir_pdf
from utils.image_utils import descargar_imagen, guardar_imagen_temporal
import os

router = APIRouter()

BUCKET_PDFS = "enfermeria"
BUCKET_FIRMAS = "firma-sello-usuarios"

@router.post("/generar_pdf_enfermeria")
async def generar_pdf_enfermeria_endpoint(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    profesional: str = Form(...),
    motivo_consulta: str = Form(...),
    hora: str = Form(...),
    temperatura: float = Form(...),
    saturacion: float = Form(...),
    ta: float = Form(...),
    tad: float = Form(...),
    frecuencia_cardiaca: float = Form(...),
    glasgow: int = Form(...),
    dolor: int = Form(...),
    glucemia: float = Form(...),
    triaje: str = Form(...),
    institucion_id: int = Form(...),
    usuario_id: str = Form(...),
):
    try:
        if not institucion_id or not usuario_id:
            return JSONResponse({"error": "Sesión inválida"}, status_code=403)

        campos = [nombre, apellido, dni, profesional, motivo_consulta, hora,
                  temperatura, saturacion, ta, tad, frecuencia_cardiaca,
                  glasgow, dolor, glucemia, triaje]
        if not all(str(c).strip() for c in campos):
            return JSONResponse({"exito": False, "mensaje": "Faltan campos obligatorios."})

        base_firma = f"firma_{usuario_id}_{institucion_id}"
        base_sello = f"sello_{usuario_id}_{institucion_id}"
        c_firma, n_firma = descargar_imagen(supabase, BUCKET_FIRMAS, base_firma)
        c_sello, n_sello = descargar_imagen(supabase, BUCKET_FIRMAS, base_sello)
        firma_path = guardar_imagen_temporal(c_firma, n_firma) if c_firma else None
        sello_path = guardar_imagen_temporal(c_sello, n_sello) if c_sello else None

        datos = {
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "profesional": profesional,
            "motivo_consulta": motivo_consulta,
            "hora": hora,
            "temperatura": temperatura,
            "saturacion": saturacion,
            "ta": ta,
            "tad": tad,
            "frecuencia_cardiaca": frecuencia_cardiaca,
            "glasgow": glasgow,
            "dolor": dolor,
            "glucemia": glucemia,
            "triaje": triaje,
        }
        pdf_path = generar_pdf_enfermeria(datos, firma_path, sello_path)
        nombre_pdf = os.path.basename(pdf_path)
        with open(pdf_path, "rb") as f:
            pdf_url = subir_pdf(BUCKET_PDFS, nombre_pdf, f)

        if firma_path and os.path.exists(firma_path):
            os.remove(firma_path)
        if sello_path and os.path.exists(sello_path):
            os.remove(sello_path)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        supabase.table("enfermeria").insert({
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "profesional": profesional,
            "motivo_consulta": motivo_consulta,
            "hora": hora,
            "temperatura": temperatura,
            "saturacion": saturacion,
            "ta": ta,
            "tad": tad,
            "frecuencia_cardiaca": frecuencia_cardiaca,
            "glasgow": glasgow,
            "dolor": dolor,
            "glucemia": glucemia,
            "triaje": triaje,
            "usuario_id": usuario_id,
            "institucion_id": institucion_id,
            "pdf_url": pdf_url,
        }).execute()

        return {"exito": True, "pdf_url": pdf_url}

    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)})

@router.post("/enviar_pdf_enfermeria")
async def enviar_pdf_enfermeria(paciente: str = Form(...), dni: str = Form(...)):
    try:
        res = supabase.table("pacientes").select("email").eq("dni", dni).single().execute()
        email = res.data.get("email") if res.data else None
        if not email:
            return JSONResponse({"exito": False, "mensaje": "No se encontró un e-mail para este DNI."}, status_code=404)

        consulta = (
            supabase.table("enfermeria")
            .select("pdf_url")
            .eq("dni", dni)
            .order("id", desc=True)
            .limit(1)
            .execute()
        )
        pdf_url = consulta.data[0]["pdf_url"] if consulta.data else None
        if not pdf_url:
            return JSONResponse({"exito": False, "mensaje": "No se encontró el PDF."}, status_code=404)

        asunto = "Registro de enfermería"
        cuerpo = f"Estimado/a {paciente}, adjuntamos el informe de enfermería."
        enviar_email_con_pdf(email_destino=email, asunto=asunto, cuerpo=cuerpo, pdf_url=pdf_url)
        return {"exito": True}
    except Exception as e:
        return JSONResponse({"exito": False, "mensaje": str(e)})
