from fpdf import FPDF
import os

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Historia Clínica", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Nombre del paciente: {data.patient_name}", ln=True)
    pdf.cell(200, 10, txt=f"Diagnóstico: {data.diagnosis}", ln=True)
    pdf.multi_cell(200, 10, txt=f"Notas: {data.notes}")

    filename = f"{data.patient_name.replace(' ', '_')}.pdf"
    output_path = os.path.join("static", filename)
    pdf.output(output_path)

    return filename
