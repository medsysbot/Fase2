README - MedSys | Sistema Médico Modular
Descripción General
MedSys es un sistema médico modular diseñado para clínicas y profesionales de la salud. Permite registrar pacientes,
generar historiales, emitir recetas y enviar documentos PDF por correo electrónico. Funciona con tecnologías modernas
y es 100% integrable a Supabase y Railway.
Tecnologías Usadas
- Backend: Python + FastAPI
- Frontend: HTML5, CSS3, JavaScript
- Base de datos: Supabase
- Emails: SMTP configurable
- Deploy: Railway
Estructura de Carpetas
/
??? main.py # Punto de entrada FastAPI
??? routes/ # Módulos backend (registro, recetas, historia clínica, etc.)
??? static/ # Archivos estáticos como estilos, scripts, PDFs
??? templates/ # Formularios HTML
??? utils/ # Funciones reutilizables
??? requirements.txt # Dependencias
??? README.md # Documentación
Cómo Desplegar en Railway
1. Crear un nuevo proyecto en Railway
2. Subir el ZIP del proyecto o conectarlo a GitHub
3. Railway detecta automáticamente:
 - Lenguaje: Python
 - Framework: FastAPI
 - Start Command: uvicorn main:app --host=0.0.0.0 --port=${PORT}
README - MedSys | Sistema Médico Modular
4. Si no lo detecta, configurarlo manualmente
5. Cargar las variables de entorno requeridas.
   Una forma rápida es copiar el archivo `.env.example` a `.env` y
   completar los valores correspondientes.
Variables de Entorno
- SUPABASE_URL (pública)
- SUPABASE_SERVICE_ROLE_KEY (privada)
- EMAIL_ORIGEN (pública)
- EMAIL_PASSWORD (privada)
- SMTP_SERVER (pública)
- SMTP_PORT (pública)
Test de Funcionamiento
GET / ? Debe responder {"status": "OK"}
POST /generate ? Enviar JSON con datos del paciente:
{
 "patient_name": "Juan Pérez",
 "diagnosis": "Hipertensión arterial",
 "notes": "Paciente estable. Controlar en 15 días."
}
Respuesta: URL del PDF generado
Notas Importantes
- La carpeta /static no debe eliminarse
- Los PDFs se guardan automáticamente ahí
- Esta versión es estable y lista para ampliaciones (firmas, QR, etc.)
- Las imágenes de firma y sello deben estar en formato PNG. Otros formatos
  generarán un error 400 al enviar los formularios.
Contacto
Desarrollado por Max & ChatGPT Codex
README - MedSys | Sistema Médico Modular
Contacto oficial: medisys.bot@gmail.com
