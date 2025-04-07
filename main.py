import whisper
import tempfile
import os
from fastapi import File, UploadFile, FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fpdf import FPDF

app = FastAPI()

# Permitir CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "MEDSYS API activa"}

# ----------------- MODELO RECETA MÉDICA -----------------

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

        # Encabezado
        pdf.set_text_color(8, 60, 74)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt="MEDSYS – RECETA MÉDICA", ln=True, align="C")

        # Cuerpo
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 12)
        pdf.ln(20)
        pdf.cell(0, 10, f"Nombre del Paciente: {data.nombre}", ln=True)
        pdf.cell(0, 10, f"DNI: {data.dni}", ln=True)
        pdf.cell(0, 10, f"Diagnóstico: {data.diagnostico}", ln=True)
        pdf.cell(0, 10, f"Fecha: {data.fecha}", ln=True)
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"Medicamentos Indicados: {data.medicamentos}")

        # Guardar PDF
        output_path = "static/doc/receta-medica-generada.pdf"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)

        return {"status": "success", "message": "Receta médica generada correctamente"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ----------------- TRANSCRIPCIÓN DE AUDIO -----------------

whisper_model = whisper.load_model("base")

@app.post("/transcribe-audio")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        result = whisper_model.transcribe(tmp_path)
        return {
            "status": "success",
            "transcription": result["text"]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
