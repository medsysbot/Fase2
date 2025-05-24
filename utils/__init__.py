from .pdf_generator import (
    generar_pdf_resumen,
    generar_pdf_paciente,
    generar_pdf_historia_completa,
    generar_pdf_receta,
)
from .email_sender import enviar_email_con_pdf

__all__ = [
    "generar_pdf_resumen",
    "generar_pdf_paciente",
    "generar_pdf_historia_completa",
    "generar_pdf_receta",
    "enviar_email_con_pdf",
]
