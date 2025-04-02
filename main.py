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
