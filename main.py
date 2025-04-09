from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fpdf import FPDF
import os

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Templates ----------------
templates = Jinja2Templates(directory="templates")

# ---------------- Ruta base ----------------
@app.get("/")
async def root():
    return {"message": "MedSys Backend funcionando correctamente"}

# ---------------- Rutas HTML (Frontend) ----------------
@app.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/registro", response_class=HTMLResponse)
async def registro(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})

@app.get("/historia", response_class=HTMLResponse)
async def historia(request: Request):
    return templates.TemplateResponse("historia.html", {"request": request})

@app.get("/historia-completa", response_class=HTMLResponse)
async def historia_completa(request: Request):
    return templates.TemplateResponse("historia-clinica-completa.html", {"request": request})

@app.get("/historia-resumen", response_class=HTMLResponse)
async def historia_resumen(request: Request):
    return templates.TemplateResponse("historia-resumen.html", {"request": request})

@app.get("/historia-evolucion", response_class=HTMLResponse)
async def historia_evolucion(request: Request):
    return templates.TemplateResponse("evolucion.html", {"request": request})

@app.get("/receta", response_class=HTMLResponse)
async def receta(request: Request):
    return templates.TemplateResponse("receta.html", {"request": request})

@app.get("/indicaciones", response_class=HTMLResponse)
async def indicaciones(request: Request):
    return templates.TemplateResponse("indicaciones.html", {"request": request})

@app.get("/turnos", response_class=HTMLResponse)
async def turnos(request: Request):
    return templates.TemplateResponse("turnos.html", {"request": request})

@app.get("/busqueda", response_class=HTMLResponse)
async def busqueda(request: Request):
    return templates.TemplateResponse("busqueda.html", {"request": request})

# ---------------- Historia Clínica Completa ----------------
@app.post("/generar-pdf-historia-completa")
async def generar_pdf_historia_completa(
    nombre: str = Form(...),
    fecha_nacimiento: str = Form(...),
    edad: str = Form(...),
    sexo: str = Form(...),
    dni: str = Form(...),
    domicilio: str = Form(...),
    telefono: str = Form(...),
    correo: str = Form(...),
    obra_social: str = Form(...),
    afiliado: str = Form(...),
    personales: str = Form(...),
    familiares: str = Form(...),
    habitos: str = Form(...),
    cronicas: str = Form(...),
    cirugias: str = Form(...),
    medicacion: str = Form(...),
    estudios: str = Form(...),
    motivo: str = Form(...),
    diagnostico: str = Form(...),
    tratamiento: str = Form(...),
    instrucciones: str = Form(...),
    proxima: str = Form(...),
    profesional: str = Form(...)
):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "Historia Clinica Completa - MedSys", ln=True)
        pdf.ln(5)

        campos = {
            "Nombre del Paciente": nombre,
            "Fecha de Nacimiento": fecha_nacimiento,
            "Edad": edad,
            "Sexo": sexo,
            "DNI": dni,
            "Domicilio": domicilio,
            "Teléfono": telefono,
            "Correo Electrónico": correo,
            "Obra Social / Prepaga": obra_social,
            "Número de Afiliado": afiliado,
            "Antecedentes Personales": personales,
            "Antecedentes Familiares": familiares,
            "Hábitos": habitos,
            "Enfermedades Crónicas": cronicas,
            "Cirugías y Hospitalizaciones": cirugias,
            "Medicación Actual": medicacion,
            "Estudios Complementarios": estudios,
            "Motivo de Consulta": motivo,
            "Diagnóstico Actual": diagnostico,
            "Tratamiento Indicado": tratamiento,
            "Instrucciones / Recomendaciones": instrucciones,
            "Fecha de Próxima Consulta": proxima,
            "Profesional": profesional
        }

        for campo, valor in campos.items():
            pdf.multi_cell(0, 10, f"{campo}: {valor}")
            pdf.ln(1)

        output_path = "static/doc/historia-clinica-completa-generada.pdf"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)
        return {"status": "success", "archivo": output_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/ver-historia-completa")
async def ver_historia_completa():
    return FileResponse("static/doc/historia-clinica-completa-generada.pdf", media_type="application/pdf")

# ---------------- Historia Clínica Resumida ----------------
@app.post("/generar-pdf-historia-resumen")
async def generar_pdf_historia_resumen(
    nombre: str = Form(...),
    dni: str = Form(...),
    fecha: str = Form(...),
    motivo: str = Form(...),
    diagnostico: str = Form(...),
    tratamiento: str = Form(...),
    profesional: str = Form(...)
):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "Historia Clínica Resumida – MedSys", ln=True)
        pdf.ln(5)

        campos = {
            "Nombre del Paciente": nombre,
            "DNI": dni,
            "Fecha": fecha,
            "Motivo de Consulta": motivo,
            "Diagnóstico": diagnostico,
            "Tratamiento": tratamiento,
            "Profesional": profesional
        }

        for campo, valor in campos.items():
            pdf.multi_cell(0, 10, f"{campo}: {valor}")
            pdf.ln(1)

        output_path = "static/doc/historia-resumen-generada.pdf"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)
        return {"status": "success", "archivo": output_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/ver-historia-resumen")
async def ver_historia_resumen():
    return FileResponse("static/doc/historia-resumen-generada.pdf", media_type="application/pdf")

# ---------------- Evolución Diaria ----------------
@app.post("/generar-pdf-evolucion")
async def generar_pdf_evolucion(nombre: str = Form(...), dni: str = Form(...), fecha: str = Form(...), evolucion: str = Form(...)):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Nombre del Paciente: {nombre}", ln=True)
        pdf.cell(0, 10, f"DNI: {dni}", ln=True)
        pdf.cell(0, 10, f"Fecha: {fecha}", ln=True)
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"Evolución Clínica:\n{evolucion}")

        output_path = "static/doc/historia-evolucion-generada.pdf"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)
        return {"status": "success", "archivo": output_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/ver-evolucion")
async def ver_evolucion():
    return FileResponse("static/doc/historia-evolucion-generada.pdf", media_type="application/pdf")

# ---------------- Receta Médica ----------------
@app.post("/generar-pdf-receta")
async def generar_pdf_receta(nombre: str = Form(...), dni: str = Form(...), fecha: str = Form(...), medicamentos: str = Form(...)):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Nombre del Paciente: {nombre}", ln=True)
        pdf.cell(0, 10, f"DNI: {dni}", ln=True)
        pdf.cell(0, 10, f"Fecha: {fecha}", ln=True)
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"Medicamentos indicados:\n{medicamentos}")

        output_path = "static/doc/receta-medica-generada.pdf"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)
        return {"status": "success", "archivo": output_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/ver-receta")
async def ver_receta():
    return FileResponse("static/doc/receta-medica-generada.pdf", media_type="application/pdf")

# ---------------- Indicaciones Médicas ----------------
@app.post("/generar-pdf-indicaciones")
async def generar_pdf_indicaciones(nombre: str = Form(...), fecha: str = Form(...), indicaciones: str = Form(...)):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Nombre del Paciente: {nombre}", ln=True)
        pdf.cell(0, 10, f"Fecha: {fecha}", ln=True)
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"Indicaciones Médicas:\n{indicaciones}")

        output_path = "static/doc/indicaciones-medicas-generado.pdf"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)
        return {"status": "success", "archivo": output_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/ver-indicaciones")
async def ver_indicaciones():
    return FileResponse("static/doc/indicaciones-medicas-generado.pdf", media_type="application/pdf")
