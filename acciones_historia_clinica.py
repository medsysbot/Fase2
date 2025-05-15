from fastapi import APIRouter, Form, Request, UploadFile, File
from fastapi.responses import JSONResponse
from fpdf import FPDF
from pathlib import Path
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from supabase import create_client

router = APIRouter()

# Configuración Supabase
SUPABASE_URL = "https://wolcdduoroiobtadbcup.supabase.com"
SUPABASE_KEY_SERVICE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndvbGNkZHVvcm9pb2J0YWRiY3VwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjIwMTQ5MywiZXhwIjoyMDYxNzc3NDkzfQ.GJtQkyj4PBLxekNQXJq7-mqnnqpcb_Gp0O0nmpLxICM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY_SERVICE)

BUCKET_PDFS = "pdfs"
BUCKET_FIRMAS = "firma-sello-usuarios"

# ---------- REGISTRAR HISTORIA CLÍNICA Y GENERAR PDF ----------
@router.post("/generar_pdf_historia_completa")
async def generar_pdf_historia_completa(
    request: Request,
    nombre: str = Form(...),
    fecha_nacimiento: str = Form(...),
    edad: str = Form(...),
    sexo: str = Form(...),
    dni: str = Form(...),
    domicilio: str = Form(""),
    telefono: str = Form(""),
    email: str = Form(""),
    obra_social: str = Form(""),
    numero_afiliado: str = Form(""),
    antecedentes_personales: str = Form(""),
    antecedentes_familiares: str = Form(""),
    habitos: str = Form(""),
    enfermedades_cronicas: str = Form(""),
    cirugias: str = Form(""),
    medicacion: str = Form(""),
    estudios: str = Form(""),
    historial_tratamientos: str = Form(""),
    historial_consultas: str = Form(""),
    firma: UploadFile = File(None),
    sello: UploadFile = File(None)
):
    try:
        institucion_id = request.session.get("institucion_id")
        if institucion_id is None:
            return JSONResponse({"error": "Sesión sin institución activa"}, status_code=403)

        safe_name = nombre.strip().replace(" ", "_")
        filename = f"historia_completa_{safe_name}_{dni}.pdf"
        local_path = os.path.join("static/doc", filename)
        Path("static/doc").mkdir(parents=True, exist_ok=True)

        # Crear PDF
        pdf = FPDF()
        pdf.add_page()
        logo_path = "static/icons/logo-medsys-gris.png"
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=10, y=4, w=60)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 40, "Historia Clínica Completa - MEDSYS", ln=True, align="C")
        pdf.set_draw_color(150, 150, 150)
        pdf.set_line_width(1)
        pdf.line(10, 50, 200, 50)
        pdf.set_font("Arial", size=12)
        pdf.ln(15)

        campos = [
            ("Nombre del Paciente", nombre),
            ("DNI", dni),
            ("Fecha de Nacimiento", fecha_nacimiento),
            ("Edad", edad),
            ("Sexo", sexo),
            ("Teléfono", telefono),
            ("Correo Electrónico", email),
            ("Domicilio", domicilio),
            ("Obra Social / Prepaga", obra_social),
            ("Número de Afiliado", numero_afiliado),
            ("Antecedentes Personales", antecedentes_personales),
            ("Antecedentes Familiares", antecedentes_familiares),
            ("Hábitos", habitos),
            ("Enfermedades Crónicas", enfermedades_cronicas),
            ("Cirugías / Hospitalizaciones", cirugias),
            ("Medicación Actual", medicacion),
            ("Estudios Complementarios", estudios),
            ("Historial de Tratamientos", historial_tratamientos),
            ("Historial de Consultas", historial_consultas)
        ]
        for label, value in campos:
            pdf.cell(0, 10, f"{label}: {value}", ln=True)

        pdf.output(local_path)

        # Subir a Supabase
        with open(local_path, "rb") as file_data:
            supabase.storage.from_(BUCKET_PDFS).upload(filename, file_data, {"content-type": "application/pdf"})

        # Subir firma y sello si existen
        firma_url = ""
        sello_url = ""

        if firma:
            firma_nombre = f"{dni}-firma.png"
            contenido = await firma.read()
            supabase.storage.from_(BUCKET_FIRMAS).upload(firma_nombre, contenido, {"content-type": firma.content_type})
            firma_url = f"{BUCKET_FIRMAS}/{firma_nombre}"

        if sello:
            sello_nombre = f"{dni}-sello.png"
            contenido = await sello.read()
            supabase.storage.from_(BUCKET_FIRMAS).upload(sello_nombre, contenido, {"content-type": sello.content_type})
            sello_url = f"{BUCKET_FIRMAS}/{sello_nombre}"

        # Guardar en base
        supabase.table("historia_clinica_completa").insert({
            "paciente_id": dni,
            "nombre": nombre,
            "dni": dni,
            "fecha_nacimiento": fecha_nacimiento,
            "edad": edad,
            "sexo": sexo,
            "telefono": telefono,
            "email": email,
            "domicilio": domicilio,
            "obra_social": obra_social,
            "numero_afiliado": numero_afiliado,
            "antecedentes_personales": antecedentes_personales,
            "antecedentes_familiares": antecedentes_familiares,
            "habitos": habitos,
            "enfermedades_cronicas": enfermedades_cronicas,
            "cirugias": cirugias,
            "medicacion": medicacion,
            "estudios": estudios,
            "historial_tratamientos": historial_tratamientos,
            "historial_consultas": historial_consultas,
            "institucion_id": institucion_id,
            "firma_url": firma_url,
            "sello_url": sello_url
        }).execute()

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_PDFS}/{filename}"
        return JSONResponse({"exito": True, "pdf_url": public_url})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ---------- ENVIAR PDF POR EMAIL ----------
@router.post("/enviar_pdf_historia_completa")
async def enviar_pdf_historia_completa(email: str = Form(...), nombre: str = Form(...), dni: str = Form(...)):
    try:
        safe_name = nombre.strip().replace(" ", "_")
        filename = f"historia_completa_{safe_name}_{dni}.pdf"
        local_path = os.path.join("static/doc", filename)

        remitente = "medisys.bot@gmail.com"
        contrasena = "yeuaugaxmdvydcou"
        asunto = "Historia Clínica Completa - MEDSYS"
        cuerpo = f"Estimado/a {nombre},\n\nAdjuntamos su historia clínica en formato PDF.\n\nSaludos,\nEquipo MEDSYS"

        mensaje = MIMEMultipart()
        mensaje["From"] = remitente
        mensaje["To"] = email
        mensaje["Subject"] = asunto
        mensaje.attach(MIMEText(cuerpo, "plain"))

        with open(local_path, "rb") as f:
            parte = MIMEApplication(f.read(), Name=filename)
            parte["Content-Disposition"] = f'attachment; filename="{filename}"'
            mensaje.attach(parte)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(remitente, contrasena)
            servidor.send_message(mensaje)

        return JSONResponse({"exito": True})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
