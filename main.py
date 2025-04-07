from fastapi import FastAPI
from fastapi.responses import FileResponse
from fpdf import FPDF
import os

app = FastAPI()

@app.get("/")
async def generar_pdf_prueba():
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.set_text_color(0, 102, 204)
        pdf.cell(200, 10, txt="PRUEBA DE VISOR PDF", ln=True, align="C")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(20)
        pdf.multi_cell(0, 10, "Este es un PDF de prueba para verificar que el visor funciona correctamente.")

        output_path = "static/doc/receta-medica-generada.pdf"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)

        return {"status": "success", "message": "PDF generado"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/ver")
async def ver_pdf():
    return FileResponse("static/doc/receta-medica-generada.pdf", media_type="application/pdf")
