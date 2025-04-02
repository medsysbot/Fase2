from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from utils import generate_pdf

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

class MedicalData(BaseModel):
    patient_name: str
    diagnosis: str
    notes: str

@app.get("/")
async def root():
    return {"status": "OK"}

@app.post("/generate")
async def create_record(data: MedicalData):
    pdf_path = generate_pdf(data)
    pdf_url = f"https://web-production.up.railway.app/static/{pdf_path}"
    return {"pdf": pdf_url}
