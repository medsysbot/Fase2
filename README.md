
README - MedSys | Sistema Médico Modular
Descripción General
MedSys es un sistema médico modular diseñado para clínicas y profesionales de la salud.
Permite registrar pacientes, generar historiales clínicos, emitir recetas y enviar documentos PDF por correo electrónico.
Funciona con tecnologías modernas y es 100% integrable con Supabase y Railway.

Tecnologías Usadas
Backend: Python + FastAPI

Frontend: HTML5, CSS3, JavaScript

Base de datos: Supabase

Emails: SMTP configurable

Deploy: Railway

Estructura de Carpetas
csharp
Copy
Edit
/
├── main.py                  # Punto de entrada de la app FastAPI
├── routes/                  # Endpoints (registro, recetas, historia clínica, etc.)
├── static/                  # Archivos estáticos (PDFs, CSS, JS)
├── templates/               # Formularios HTML
├── utils/                   # Funciones reutilizables
├── requirements.txt         # Dependencias del proyecto
└── README.md                # Este documento
Cómo Desplegar en Railway
Crear un nuevo proyecto en Railway.

Subir el ZIP del backend o conectar el repositorio de GitHub.

Railway detecta automáticamente:

Lenguaje: Python

Framework: FastAPI

Start Command:

nginx
Copy
Edit
uvicorn main:app --host=0.0.0.0 --port=${PORT}
Si no lo detecta, configurarlo manualmente.

Cargar las variables de entorno requeridas.

Variables de Entorno
Nombre	Tipo	Descripción
SUPABASE_URL	Pública	URL del proyecto Supabase
SUPABASE_SERVICE_ROLE_KEY	Privada	Clave secreta de Supabase
EMAIL_ORIGEN	Pública	Correo remitente del sistema
EMAIL_PASSWORD	Privada	Contraseña de ese correo
SMTP_SERVER	Pública	Servidor SMTP (ej: smtp.gmail.com)
SMTP_PORT	Pública	Puerto SMTP (ej: 587)

Test de Funcionamiento
GET /
Debe responder:

json
Copy
Edit
{ "status": "OK" }
POST /generate
Enviar un JSON como este:

json
Copy
Edit
{
  "patient_name": "Juan Pérez",
  "diagnosis": "Hipertensión arterial",
  "notes": "Paciente estable. Controlar en 15 días."
}
Respuesta esperada:

json
Copy
Edit
{
  "pdf": "https://<tu-app>.railway.app/static/Juan_Perez.pdf"
}
Notas Importantes
La carpeta /static no debe eliminarse, ya que almacena los archivos PDF generados.

El sistema está listo para ser ampliado con módulos como firmas digitales, código QR, recetas y más.

Compatible con Codex para automatización de desarrollo.

Contacto
Desarrollado por: Max & ChatGPT Codex
Correo oficial: medisys.bot@gmail.com
