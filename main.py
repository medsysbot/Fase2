from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
import tempfile
from dotenv import load_dotenv


def generar_env_automatico():
    """Crea un archivo .env con las variables del entorno si no existe."""
    env_path = ".env"
    if os.path.exists(env_path):
        return

    posibles_vars = []
    ejemplo = ".env.example"
    if os.path.exists(ejemplo):
        with open(ejemplo) as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#") or "=" not in linea:
                    continue
                posibles_vars.append(linea.split("=", 1)[0])

    extras = [
        "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "DATABASE_URL",
        "user",
        "password",
        "host",
        "port",
        "dbname",
    ]
    for var in extras:
        if var not in posibles_vars:
            posibles_vars.append(var)

    with open(env_path, "w") as f:
        for var in posibles_vars:
            valor = os.getenv(var, "")
            if not valor and var in {"user", "password", "host", "port", "dbname"}:
                db_url = os.getenv("DATABASE_URL", "")
                if db_url:
                    from urllib.parse import urlparse

                    parsed = urlparse(db_url)
                    mapping = {
                        "user": parsed.username,
                        "password": parsed.password,
                        "host": parsed.hostname,
                        "port": str(parsed.port or ""),
                        "dbname": parsed.path.lstrip("/"),
                    }
                    valor = mapping.get(var, "")
            f.write(f"{var}={valor}\n")


generar_env_automatico()
import asyncio
from utils.supabase_helper import supabase, SUPABASE_URL
from utils.db_setup import prepare_consultas_table
load_dotenv()
prepare_consultas_table()
# ╔════════════════════════════════════╗
# ║             APP BASE               ║
# ╚════════════════════════════════════╝
app = FastAPI()

# ╔════════════════════════════════════╗
# ║                CORS                ║
# ╚════════════════════════════════════╝
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ╔════════════════════════════════════╗
# ║        SESIÓN DE USUARIOS         ║
# ╚════════════════════════════════════╝
app.add_middleware(SessionMiddleware, secret_key="clave-super-secreta")

# ╔════════════════════════════════════╗
# ║        CLIENTE SUPABASE           ║
# ╚════════════════════════════════════╝
# El cliente de Supabase se obtiene desde utils.supabase_helper
# ╔════════════════════════════════════╗
# ║       ARCHIVOS ESTÁTICOS          ║
# ╚════════════════════════════════════╝
app.mount("/static", StaticFiles(directory="static"), name="static")

# ╔════════════════════════════════════╗
# ║            PLANTILLAS             ║
# ╚════════════════════════════════════╝
templates = Jinja2Templates(directory="templates")

# ╔════════════════════════════════════╗
# ║          SPLASH INICIAL           ║
# ╚════════════════════════════════════╝
@app.get("/", response_class=HTMLResponse)
async def root_redirect(request: Request):
    return templates.TemplateResponse("splash_screen.html", {"request": request})

@app.get("/splash-screen", response_class=HTMLResponse)
async def splash_inicio(request: Request):
    return templates.TemplateResponse("splash_screen.html", {"request": request})

# ╔════════════════════════════════════╗
# ║               LOGIN               ║
# ╚════════════════════════════════════╝
@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(request: Request, usuario: str = Form(...), contrasena: str = Form(...), rol: str = Form(...)):
    try:
        result = supabase.table("usuarios").select("*")\
            .eq("usuario", usuario)\
            .eq("contrasena", contrasena)\
            .eq("rol", rol)\
            .eq("activo", True)\
            .single().execute()
        user = result.data

        if user:
            request.session["usuario"] = usuario
            request.session["rol"] = rol
            request.session["nombres"] = user.get("nombres", "")
            request.session["apellido"] = user.get("apellido", "")
            request.session["institucion_id"] = user.get("institucion_id", None)
            return RedirectResponse(url="/splash-final", status_code=303)
        else:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Usuario o contraseña incorrectos"
            })

    except Exception as e:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": f"Error de conexión o datos inválidos: {str(e)}"
        })
# ╔════════════════════════════════════╗
# ║               LOGOUT              ║
# ╚════════════════════════════════════╝
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

# ╔════════════════════════════════════╗
# ║           SPLASH FINAL            ║
# ╚════════════════════════════════════╝
@app.get("/splash-final", response_class=HTMLResponse)
async def splash_final(request: Request):
    usuario_logueado = request.session.get("usuario")

    if not usuario_logueado:
        return templates.TemplateResponse("splash_final.html", {
            "request": request,
            "nombre": "Invitado",
            "titulo": ""
        })

    try:
        result = supabase.table("usuarios").select("nombres, apellido, rol")\
            .eq("usuario", usuario_logueado)\
            .single().execute()
        data = result.data or {}
        nombres = data.get("nombres", "Invitado")
        apellido = data.get("apellido", "")
        rol = data.get("rol", "desconocido")

    except Exception:
        nombres, apellido, rol = "Invitado", "", "desconocido"

    titulo = "Doctora" if rol in ["medico", "director"] else "Sra." if rol == "secretaria" else ""

    return templates.TemplateResponse("splash_final.html", {
        "request": request,
        "nombre": f"{nombres} {apellido}",
        "titulo": titulo
    })


@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    usuario = request.session.get("usuario")
    rol = request.session.get("rol")
    if not usuario or rol != "director":
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})

# ╔════════════════════════════════════╗
# ║       ARCHIVOS MÉDICOS            ║
# ╚════════════════════════════════════╝
@app.get("/listar-estudios")
async def listar_estudios():
    try:
        archivos = supabase.storage.from_("estudios-medicos").list()
        nombres = [a.get("name") for a in archivos]
        return {"archivos": nombres}
    except Exception:
        raise HTTPException(status_code=404, detail="Directorio no encontrado")

@app.post("/eliminar-estudio")
async def eliminar_estudio(nombre_archivo: str = Form(...)):
    try:
        supabase.storage.from_("estudios-medicos").remove(nombre_archivo)
        return {"status": "success", "message": "Archivo eliminado"}
    except Exception:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

@app.get("/descargar-estudio/{nombre_archivo}")
async def descargar_estudio(nombre_archivo: str):
    try:
        contenido = supabase.storage.from_("estudios-medicos").download(nombre_archivo)
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(contenido)
        tmp.close()
        return FileResponse(tmp.name, media_type="application/pdf", filename=nombre_archivo)
    except Exception:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

@app.post("/subir-estudio")
async def subir_estudio(archivo: UploadFile = File(...)):
    extensiones_permitidas = [".pdf", ".jpg", ".jpeg", ".png"]
    extension = os.path.splitext(archivo.filename)[1].lower()
    if extension not in extensiones_permitidas:
        raise HTTPException(status_code=400, detail="Formato no permitido")
    contenido = await archivo.read()
    supabase.storage.from_("estudios-medicos").upload(archivo.filename, contenido, {"content-type": archivo.content_type})
    return {"status": "success", "message": "Archivo subido correctamente"}

# ╔════════════════════════════════════╗
# ║         RUTA ALERT MANAGER        ║
# ╚════════════════════════════════════╝
@app.get("/alertas", response_class=HTMLResponse)
async def mostrar_alertas(request: Request):
    return templates.TemplateResponse("alertas.html", {"request": request})

# ╔════════════════════════════════════╗
# ║     INCLUIR RUTAS EXTERNAS        ║
# ╚════════════════════════════════════╝
from routes import (
    pacientes_router,
    historia_clinica_resumida_router,
    recetas_medicas_router,
    historia_clinica_router,
    indicaciones_medicas_router,
    consulta_diaria_router,
    turnos_router,
    busqueda_router,
    estudios_router,
    admin_router,
    paginas_router,
    solicitar_turnos_publico_router
)

from routes.acciones_estudios import iniciar_monitor
app.include_router(pacientes_router)
app.include_router(historia_clinica_router)
app.include_router(historia_clinica_resumida_router)
app.include_router(recetas_medicas_router)
app.include_router(indicaciones_medicas_router)
app.include_router(consulta_diaria_router)
app.include_router(turnos_router)
app.include_router(busqueda_router)
app.include_router(estudios_router)
app.include_router(admin_router)
app.include_router(paginas_router)
app.include_router(solicitar_turnos_publico_router, prefix="/turnos-publico")


@app.on_event("startup")
async def startup_event():
    await iniciar_monitor()
