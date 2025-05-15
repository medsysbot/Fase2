import smtplib
import ssl
import requests
from email.message import EmailMessage
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_ORIGEN = os.getenv("EMAIL_ORIGEN")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def enviar_email_con_pdf(email_destino, asunto, cuerpo, url_pdf):
    try:
        response = requests.get(url_pdf)
        if response.status_code != 200:
            raise Exception("No se pudo descargar el PDF.")

        pdf_data = response.content

        mensaje = EmailMessage()
        mensaje["From"] = EMAIL_ORIGEN
        mensaje["To"] = email_destino
        mensaje["Subject"] = asunto
        mensaje.set_content(cuerpo)

        mensaje.add_attachment(pdf_data, maintype="application", subtype="pdf", filename="historia_clinica.pdf")

        contexto = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=contexto) as server:
            server.login(EMAIL_ORIGEN, EMAIL_PASSWORD)
            server.send_message(mensaje)

        print(f"Correo enviado a {email_destino}")

    except Exception as e:
        print(f"Error al enviar correo: {e}")
        raise
