from fpdf import FPDF
import os

def generate_pdf(data):
    filename = f"{data.patient_name.replace(' ', '_')}.pdf"
    folder = "static"
    os.makedirs(folder, exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Historia Clínica", ln=True)
    pdf.cell(200, 10, txt=f"Paciente: {data.patient_name}", ln=True)
    pdf.cell(200, 10, txt=f"Diagnóstico: {data.diagnosis}", ln=True)
    pdf.multi_cell(200, 10, txt=f"Notas: {data.notes}")

    path = os.path.join(folder, filename)
    pdf.output(path)
    return filename
