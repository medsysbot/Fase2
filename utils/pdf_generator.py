from fpdf import FPDF
import os

def generar_pdf_resumen(datos, firma_path=None, sello_path=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_title("Historia Clínica Resumida")

    pdf.cell(200, 10, txt="Historia Clínica Resumida", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Paciente: {datos['paciente']}", ln=True)
    pdf.cell(200, 10, txt=f"DNI: {datos['dni']}", ln=True)
    pdf.cell(200, 10, txt=f"Edad: {datos['edad']}", ln=True)
    pdf.ln(5)

    pdf.multi_cell(0, 10, f"Motivo de consulta:\n{datos['motivo']}\n")
    pdf.multi_cell(0, 10, f"Diagnóstico:\n{datos['diagnostico']}\n")
    pdf.multi_cell(0, 10, f"Tratamiento:\n{datos['tratamiento']}\n")
    pdf.multi_cell(0, 10, f"Observaciones:\n{datos['observaciones']}\n")

    if firma_path and os.path.exists(firma_path):
        pdf.ln(10)
        pdf.cell(200, 10, txt="Firma del Profesional:", ln=True)
        pdf.image(firma_path, x=10, y=pdf.get_y(), w=40)
        pdf.ln(25)

    if sello_path and os.path.exists(sello_path):
        pdf.cell(200, 10, txt="Sello del Profesional:", ln=True)
        pdf.image(sello_path, x=60, y=pdf.get_y(), w=40)
        pdf.ln(25)

    filename = f"{datos['dni']}_resumen.pdf"
    output_path = os.path.join("/tmp", filename)
    pdf.output(output_path)

    return output_path
