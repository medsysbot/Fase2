from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
from supabase import create_client

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Sesiones ----------------
app.add_middleware(SessionMiddleware, secret_key="clave-super-secreta")

# ---------------- Supabase Client ----------------
SUPABASE_URL = "https://wolcdduoroiobtadbcup.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndvbGNkZHVvcm9pb2J0YWRiY3VwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYyMDE0OTMsImV4cCI6MjA2MTc3NzQ5M30.rV_1sa8iM8s6eCD-5m_wViCgWpd0d2xRHA_zQxRabHU"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- Archivos estáticos ----------------
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- Templates ----------------
templates = Jinja2Templates(directory="templates")

# ---------------- RUTA SPLASH INICIAL ----------------
@app.get("/", response_class=HTMLResponse)
async def root_redirect(request: Request):
    return templates.TemplateResponse("splash_screen.html", {"request": request})

@app.get("/splash-screen", response_class=HTMLResponse)
async def splash_inicio(request: Request):
    return templates.TemplateResponse("splash_screen.html", {"request": request})

# ---------------- LOGIN usando SUPABASE ----------------
@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(request: Request, usuario: str = Form(...), contrasena: str = Form(...), rol: str = Form(...)):
    data, error = supabase.table("usuarios").select("*").eq("usuario", usuario).eq("contrasena", contrasena).eq("rol", rol).eq("activo", True).single().execute()

    if data.data:
        user = data.data
        request.session.update({
            "usuario": usuario,
            "rol": rol,
            "nombres": user["nombres"],
            "apellido": user["apellido"],
            "institucion_id": user["institucion_id"]
        })
        return RedirectResponse(url="/splash-final", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Usuario o contraseña incorrectos"
        })

# ---------------- SPLASH FINAL usando SUPABASE ----------------
@app.get("/splash-final", response_class=HTMLResponse)
async def splash_final(request: Request):
    usuario_logueado = request.session.get("usuario")

    if not usuario_logueado:
        return templates.TemplateResponse("splash_final.html", {
            "request": request,
            "nombre": "Invitado",
            "titulo": ""
        })

    data, error = supabase.table("usuarios").select("nombres, apellido, rol").eq("usuario", usuario_logueado).single().execute()

    if data.data:
        nombres, apellido, rol = data.data["nombres"], data.data["apellido"], data.data["rol"]
    else:
        nombres, apellido, rol = "Invitado", "", "desconocido"

    titulo = "Doctora" if rol in ["medico", "director"] else "Sra." if rol == "secretaria" else ""

    return templates.TemplateResponse("splash_final.html", {
        "request": request,
        "nombre": f"{nombres} {apellido}",
        "titulo": titulo
    })

# ---------------- RUTAS HTML y demás funcionalidades (sin cambios) ----------------
from admin_routes import router as admin_router
app.include_router(admin_router)

from acciones_pacientes import router as pacientes_router
app.include_router(pacientes_router)
