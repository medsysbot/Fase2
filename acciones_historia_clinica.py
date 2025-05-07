from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from fpdf import FPDF
from pathlib import Path
import os
from supabase import create_client

# ╔══════════════════════════════════════════════╗
# ║    RUTAS PARA HISTORIA CLÍNICA COMPLETA      ║
# ╚══════════════════════════════════════════════╝
router = APIRouter()

# ╔════════════════════════════════════╗
# ║     CONFIGURACIÓN DE SUPABASE     ║
# ╚════════════════════════════════════╝
SUPABASE_URL = "https://wolcdduoroiobtadbcup.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET_PDFS = "pdfs"

# ╔══════════════════════════════════════════════╗
# ║  REGISTRAR HISTORIA CLÍNICA Y GENERAR PDF    ║
# ╚══════════════════════════════════════════════╝
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
    historial_consultas: str = Form("")
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
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Historia Clínica Completa - MEDSYS", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.ln(10)

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

        # Guardar en tabla historia_clinica_completa
        supabase.table("historia_clinica_completa").insert({
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
            "institucion_id": institucion_id
        }).execute()

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_PDFS}/{filename}"
        return JSONResponse({"exito": True, "pdf_url": public_url})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
