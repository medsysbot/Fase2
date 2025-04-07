from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fpdf import FPDF
import os

app = FastAPI()

# CORS para permitir acceso desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# RUTA BASE DE PRUEBA
@app.get("/")
async def root():
    return {"message": "MedSys Backend funcionando correctamente"}

# RECETA MÉDICA – GENERAR PDF
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

# INDICACIONES MÉDICAS – GENERAR PDF
@app.post("/generar-pdf-indicaciones")
async def generar_pdf_indicaciones(nombre: str = Form(...), dni: str = Form(...), fecha: str = Form(...), indicaciones: str = Form(...)):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Nombre del Paciente: {nombre}", ln=True)
        pdf.cell(0, 10, f"DNI: {dni}", ln=True)
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

# HISTORIA CLÍNICA – EVOLUCIÓN DIARIA (Modelo Base)
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

        output_path = "static/doc/historia-evolucion-diaria-generada.pdf"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)

        return {"status": "success", "archivo": output_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/ver-evolucion")
async def ver_evolucion():
    return FileResponse("static/doc/historia-evolucion-diaria-generada.pdf", media_type="application/pdf")
