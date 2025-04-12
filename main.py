from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fpdf import FPDF
import sqlite3
import os
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
if DEBUG:
    logging.info("✅ MedSys se está ejecutando en modo DESARROLLO")

app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Archivos Estáticos (Ruta absoluta para Railway)
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Clase PDF Base
class MedSysPDF(FPDF):
    def header(self):
        try:
            self.image("static/icons/logo1.png", x=10, y=8, w=30)
        except:
            logging.error("Logo no encontrado para el PDF.")
        self.set_font("Arial", 'B', 14)
        self.cell(0, 10, "MedSys - Documento Médico", ln=True, align="C")
        self.ln(20)

    def cuerpo(self, campos: dict):
        self.set_font("Arial", '', 12)
        for campo, valor in campos.items():
            self.multi_cell(0, 10, f"{campo}: {valor}")
            self.ln(1)

# Verificación por Rol (Simulada)
def get_rol(request: Request):
    return request.query_params.get("rol", "invitado")

def rol_requerido(roles_permitidos):
    def wrapper(request: Request):
        rol_actual = get_rol(request)
        if rol_actual not in roles_permitidos:
            raise HTTPException(status_code=403, detail="Acceso no autorizado para este rol")
    return Depends(wrapper)

# Ruta Base Redirige al Splash
@app.get("/")
async def root():
    return RedirectResponse(url="/splash")

@app.get("/check-db")
async def check_db():
    try:
        conn = sqlite3.connect("/app/static/doc/medsys.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = cursor.fetchall()
        conn.close()
        return {"status": "success", "tablas": tablas}
    except Exception as e:
        logging.error(f"Error de base de datos: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/splash", response_class=HTMLResponse)
async def splash(request: Request):
    return templates.TemplateResponse("splash_screen.html", {"request": request})

@app.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/registro", response_class=HTMLResponse, dependencies=[rol_requerido(["secretaria", "director"])])
async def registro(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})

@app.get("/historia", response_class=HTMLResponse, dependencies=[rol_requerido(["medico", "director"])])
async def historia(request: Request):
    return templates.TemplateResponse("historia.html", {"request": request})

@app.get("/historia-completa", response_class=HTMLResponse, dependencies=[rol_requerido(["medico", "director"])])
async def historia_completa(request: Request):
    return templates.TemplateResponse("historia-clinica-completa.html", {"request": request})

@app.get("/historia-resumen", response_class=HTMLResponse, dependencies=[rol_requerido(["medico", "director"])])
async def historia_resumen(request: Request):
    return templates.TemplateResponse("historia-resumen.html", {"request": request})

@app.get("/historia-evolucion", response_class=HTMLResponse, dependencies=[rol_requerido(["medico", "director"])])
async def historia_evolucion(request: Request):
    return templates.TemplateResponse("historia-evolucion.html", {"request": request})

@app.get("/receta", response_class=HTMLResponse, dependencies=[rol_requerido(["medico", "director"])])
async def receta(request: Request):
    return templates.TemplateResponse("receta.html", {"request": request})

@app.get("/indicaciones", response_class=HTMLResponse, dependencies=[rol_requerido(["medico", "director"])])
async def indicaciones(request: Request):
    return templates.TemplateResponse("indicaciones.html", {"request": request})

@app.get("/turnos", response_class=HTMLResponse, dependencies=[rol_requerido(["secretaria", "director"])])
async def turnos(request: Request):
    return templates.TemplateResponse("turnos.html", {"request": request})

@app.get("/busqueda", response_class=HTMLResponse, dependencies=[rol_requerido(["secretaria", "director"])])
async def busqueda(request: Request):
    return templates.TemplateResponse("busqueda.html", {"request": request})

@app.get("/estudios", response_class=HTMLResponse, dependencies=[rol_requerido(["director"])])
async def estudios(request: Request):
    return templates.TemplateResponse("estudios.html", {"request": request})

@app.get("/prueba", response_class=HTMLResponse)
async def prueba():
    return "<h1>Prueba exitosa</h1>"
