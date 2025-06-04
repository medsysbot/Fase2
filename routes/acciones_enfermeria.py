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
    presion_arterial: str = Form(...),
    observaciones: str = Form(...),
):
    try:
        usuario = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario:
            return JSONResponse({"error": "Sesión inválida"}, status_code=403)

        campos = [nombre, apellido, dni, profesional, motivo_consulta, hora,
                  temperatura, saturacion, ta, tad, frecuencia_cardiaca,
                  glasgow, dolor, glucemia, triaje,
                  presion_arterial, observaciones]
        if not all(str(c).strip() for c in campos):
            return JSONResponse({"exito": False, "mensaje": "Faltan campos obligatorios."})

        base_firma = f"firma_{usuario}_{institucion_id}"
        base_sello = f"sello_{usuario}_{institucion_id}"
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
            "presion_arterial": presion_arterial,
            "observaciones": observaciones,
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
            "presion_arterial": presion_arterial,
            "observaciones": observaciones,
            "usuario_id": usuario,
            "institucion_id": int(institucion_id),
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

# ╔════════════════════════════════════╗
# ║        GUARDAR FORMULARIO         ║
# ╚════════════════════════════════════╝
@router.post("/guardar_enfermeria")
async def guardar_enfermeria(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    dni: str = Form(...),
    edad: str = Form(...),
    altura: str = Form(...),
    peso: str = Form(...),
    hora: str = Form(...),
    temperatura: str = Form(...),
    glucemia: str = Form(...),
    glasgow: str = Form(...),
    saturacion: str = Form(...),
    frecuencia_cardiaca: str = Form(...),
    ta: str = Form(...),
    tad: str = Form(...),
    dolor: str = Form(...),
    triaje: str = Form(...),
    motivo_consulta: str = Form(...),
    profesional: str = Form(...),
    presion_arterial: str = Form(...),
    observaciones: str = Form(...)
):
    try:
        usuario_id = request.session.get("usuario")
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None or not usuario_id:
            return JSONResponse({"error": "Sesión inválida o expirada"}, status_code=403)

        data = {
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "edad": edad,
            "altura": altura,
            "peso": peso,
            "hora": hora,
            "temperatura": temperatura,
            "glucemia": glucemia,
            "glasgow": glasgow,
            "saturacion": saturacion,
            "frecuencia_cardiaca": frecuencia_cardiaca,
            "ta": ta,
            "tad": tad,
            "dolor": dolor,
            "triaje": triaje,
            "motivo_consulta": motivo_consulta,
            "profesional": profesional,
            "presion_arterial": presion_arterial,
            "observaciones": observaciones,
            "usuario_id": usuario_id,
            "institucion_id": int(institucion_id)
        }

        supabase.table("enfermeria").insert(data).execute()
        return {"message": "Guardado exitosamente"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
