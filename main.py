import whisper
import tempfile
from fastapi import File, UploadFile
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir CORS para pruebas desde Postman u otras apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de receta médica
class Prescription(BaseModel):
    patient_name: str
    diagnosis: str
    notes: str

# Endpoint para crear receta médica
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

# Endpoint base de prueba (opcional)
@app.get("/")
async def root():
    return {"message": "MEDSYS API activa"}
# Cargar modelo Whisper (una vez al iniciar)
whisper_model = whisper.load_model("base")

@app.post("/transcribe-audio")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await file.read())
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
