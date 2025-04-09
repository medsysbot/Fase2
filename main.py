from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fpdf import FPDF
import sqlite3
import os

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Templates ----------------
templates = Jinja2Templates(directory="templates")

# ---------------- Clase PDF Base ----------------
class MedSysPDF(FPDF):
    def header(self):
        try:
            self.image("static/icons/logo1.png", x=10, y=8, w=30)
        except:
            pass
        self.set_font("Arial", 'B', 14)
        self.cell(0, 10, "MedSys - Documento Médico", ln=True, align="C")
        self.ln(20)

    def cuerpo(self, campos: dict):
        self.set_font("Arial", '', 12)
        for campo, valor in campos.items():
            self.multi_cell(0, 10, f"{campo}: {valor}")
            self.ln(1)

# ---------------- Ruta base ----------------
@app.get("/")
async def root():
    return {"message": "MedSys Backend funcionando correctamente"}

# ---------------- Rutas HTML (Frontend) ----------------
@app.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/registro", response_class=HTMLResponse)
async def registro(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})

@app.get("/historia", response_class=HTMLResponse)
async def historia(request: Request):
    return templates.TemplateResponse("historia.html", {"request": request})

@app.get("/historia-completa", response_class=HTMLResponse)
async def historia_completa(request: Request):
    return templates.TemplateResponse("historia-clinica-completa.html", {"request": request})

@app.get("/historia-resumen", response_class=HTMLResponse)
async def historia_resumen(request: Request):
    return templates.TemplateResponse("historia-resumen.html", {"request": request})

@app.get("/historia-evolucion", response_class=HTMLResponse)
async def historia_evolucion(request: Request):
    return templates.TemplateResponse("evolucion.html", {"request": request})

@app.get("/receta", response_class=HTMLResponse)
async def receta(request: Request):
    return templates.TemplateResponse("receta.html", {"request": request})

@app.get("/indicaciones", response_class=HTMLResponse)
async def indicaciones(request: Request):
    return templates.TemplateResponse("indicaciones.html", {"request": request})

@app.get("/turnos", response_class=HTMLResponse)
async def turnos(request: Request):
    return templates.TemplateResponse("turnos.html", {"request": request})

@app.get("/busqueda", response_class=HTMLResponse)
async def busqueda(request: Request):
    return templates.TemplateResponse("busqueda.html", {"request": request})

# ---------------- Registro de Pacientes con Base de Datos ----------------
@app.post("/registrar-paciente")
async def registrar_paciente(
    nombre: str = Form(...),
    fecha_nacimiento: str = Form(...),
    dni: str = Form(...),
    direccion: str = Form(...),
    telefono: str = Form(...),
    obra_social: str = Form(...),
    sexo: str = Form(...),
    contacto_emergencia: str = Form(...)
):
    try:
        conn = sqlite3.connect("static/doc/medsys.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO pacientes (
                nombre, fecha_nacimiento, dni, direccion, telefono, obra_social, sexo, contacto_emergencia
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nombre,
            fecha_nacimiento,
            dni,
            direccion,
            telefono,
            obra_social,
            sexo,
            contacto_emergencia
        ))

        conn.commit()
        conn.close()

        return {"status": "success", "message": "Paciente registrado correctamente"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ---------------- Guardar en historial clínico al generar PDF ----------------

def guardar_en_historial(nombre, dni, fecha, tipo_documento, detalle, archivo_pdf):
    conn = sqlite3.connect("static/doc/medsys.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO historial (nombre, dni, fecha, tipo_documento, detalle, archivo_pdf)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nombre, dni, fecha, tipo_documento, detalle, archivo_pdf))
    conn.commit()
    conn.close()

@app.post("/generar-pdf-receta")
async def generar_pdf_receta(nombre: str = Form(...), dni: str = Form(...), fecha: str = Form(...), medicamentos: str = Form(...)):
    try:
        pdf = MedSysPDF()
        pdf.add_page()
        campos = {
            "Nombre del Paciente": nombre,
            "DNI": dni,
            "Fecha": fecha,
            "Medicamentos indicados": medicamentos
        }
        pdf.cuerpo(campos)

        filename = f"receta_{dni}_{fecha}.pdf"
        output_path = f"static/doc/{filename}"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)

        guardar_en_historial(nombre, dni, fecha, "Receta Médica", medicamentos, filename)

        return {"status": "success", "archivo": output_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/ver-receta")
async def ver_receta():
    return FileResponse("static/doc/receta-medica-generada.pdf", media_type="application/pdf")
