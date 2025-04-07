from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fpdf import FPDF
import whisper
import tempfile
import os

app = FastAPI()

# Permitir CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint raíz
@app.get("/")
async def root():
    return {"message": "MEDSYS API activa"}

# ----------------- MODELO DE INDICACIONES -----------------

class IndicacionesModel(BaseModel):
    nombre: str
    dni: str
    fecha: str
    indicaciones: str

@app.post("/generar-pdf-indicaciones")
async def generar_pdf_indicaciones(data: IndicacionesModel):
    try:
        class PDF(FPDF):
            def header(self):
                self.image("static/icons/logo1.png", x=10, y=8, w=25)
                self.set_font("Arial", "B", 16)
                self.set_text_color(8, 60, 74)
                self.cell(0, 10, "MEDSYS – INDICACIONES MÉDICAS", ln=True, align="C")
                self.ln(15)

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", "", 12)
        pdf.set_text_color(0, 0, 0)

        pdf.cell(0, 10, f"Nombre del Paciente: {data.nombre}", ln=True)
        pdf.cell(0, 10, f"DNI: {data.dni}", ln=True)
        pdf.cell(0, 10, f"Fecha: {data.fecha}", ln=True)
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"Indicaciones: {data.indicaciones}")

        output_path = "static/doc/indicaciones-medicas-generado.pdf"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)

        return {"status": "success", "message": "PDF generado correctamente"}
    
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

# ----------------- MODELO RECETA DE DEMO -----------------

class Prescription(BaseModel):
    patient_name: str
    diagnosis: str
    notes: str

@app.post("/prescriptions")
async def create_prescription(prescription: Prescription):
    return {
        "status": "success",
        "data": {
            "patient": prescription.patient_name,
            "diagnosis": prescription.diagnosis,
            "notes": prescription.notes
        }
    }
