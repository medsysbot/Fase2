import whisper
import tempfile
import os
from fastapi import File, UploadFile, FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fpdf import FPDF

app = FastAPI()

# Middleware CORS (opcional para pruebas externas)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Archivos estáticos (CSS, JS, iconos, PDFs)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------------- RUTAS FRONTEND ----------------------

@app.get("/", response_class=HTMLResponse)
async def splash():
    return FileResponse("templates/splash_screen.html")

@app.get("/index", response_class=HTMLResponse)
async def menu():
    return FileResponse("templates/index.html")

@app.get("/registro", response_class=HTMLResponse)
async def registro():
    return FileResponse("templates/registro.html")

@app.get("/historia", response_class=HTMLResponse)
async def historia():
    return FileResponse("templates/historia.html")

@app.get("/historia-completa", response_class=HTMLResponse)
async def historia_completa():
    return FileResponse("templates/historia-completa.html")

@app.get("/historia-resumen", response_class=HTMLResponse)
async def historia_resumen():
    return FileResponse("templates/historia-resumen.html")

@app.get("/historia-evolucion", response_class=HTMLResponse)
async def historia_evolucion():
    return FileResponse("templates/historia-evolucion.html")

@app.get("/receta", response_class=HTMLResponse)
async def receta():
    return FileResponse("templates/receta.html")

@app.get("/indicaciones", response_class=HTMLResponse)
async def indicaciones():
    return FileResponse("templates/indicaciones.html")

@app.get("/turnos", response_class=HTMLResponse)
async def turnos():
    return FileResponse("templates/turnos.html")

@app.get("/busqueda", response_class=HTMLResponse)
async def busqueda():
    return FileResponse("templates/busqueda.html")

# ---------------------- MODELOS PDF ----------------------

class RecetaModel(BaseModel):
    nombre: str
    dni: str
    diagnostico: str
    fecha: str
    medicamentos: str

@app.post("/generar-pdf-receta")
async def generar_pdf_receta(data: RecetaModel):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Logo
        pdf.image("static/icons/logo1.png", x=10, y=8, w=30)

        pdf.set_text_color(8, 60, 74)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt="MEDSYS – RECETA MÉDICA", ln=True, align="C")

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.ln(20)
        pdf.cell(0, 10, f"Nombre del Paciente: {data.nombre}", ln=True)
        pdf.cell(0, 10, f"DNI: {data.dni}", ln=True)
        pdf.cell(0, 10, f"Diagnóstico: {data.diagnostico}", ln=True)
        pdf.cell(0, 10, f"Fecha: {data.fecha}", ln=True)
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"Medicamentos Indicados: {data.medicamentos}")

        output_path = "static/doc/receta-medica-generada.pdf"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)

        return {"status": "success", "message": "PDF de receta generado"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

class IndicacionesModel(BaseModel):
    nombre: str
    dni: str
    fecha: str
    indicaciones: str

@app.post("/generar-pdf-indicaciones")
async def generar_pdf_indicaciones(data: IndicacionesModel):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Logo
        pdf.image("static/icons/logo1.png", x=10, y=8, w=30)

        pdf.set_text_color(8, 60, 74)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt="MEDSYS – INDICACIONES MÉDICAS", ln=True, align="C")

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.ln(20)
        pdf.cell(0, 10, f"Nombre del Paciente: {data.nombre}", ln=True)
        pdf.cell(0, 10, f"DNI: {data.dni}", ln=True)
        pdf.cell(0, 10, f"Fecha: {data.fecha}", ln=True)
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"Indicaciones: {data.indicaciones}")

        output_path = "static/doc/indicaciones-medicas-generado.pdf"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)

        return {"status": "success", "message": "PDF de indicaciones generado"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ---------------------- TRANSCRIPCIÓN ----------------------

whisper_model = whisper.load_model("base")

@app.post("/transcribe-audio")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        result = whisper_model.transcribe(tmp_path)
        return {"status": "success", "transcription": result["text"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}
