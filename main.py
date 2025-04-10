from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
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

# ---------------- Verificación por Rol (Simulada) ----------------
def get_rol(request: Request):
    # En el futuro esto se obtendrá de una sesión o token
    return request.query_params.get("rol", "invitado")

def rol_requerido(roles_permitidos):
    def wrapper(request: Request):
        rol_actual = get_rol(request)
        if rol_actual not in roles_permitidos:
            raise HTTPException(status_code=403, detail="Acceso no autorizado para este rol")
    return Depends(wrapper)

# ---------------- Ruta base ----------------
@app.get("/")
async def root():
    return RedirectResponse(url="/splash")

# ---------------- Ruta para verificación de BD ----------------
@app.get("/check-db")
async def check_db():
    try:
        conn = sqlite3.connect("static/doc/medsys.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = cursor.fetchall()
        conn.close()
        return {"status": "success", "tablas": tablas}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ---------------- Rutas HTML (Frontend) ----------------
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
    return templates.TemplateResponse("evolucion.html", {"request": request})

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

