from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
from supabase import create_client, Client

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

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
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

# ╔════════════════════════════════════╗
# ║             RUTAS HTML            ║
# ╚════════════════════════════════════╝
@app.get("/busqueda", response_class=HTMLResponse)
async def busqueda(request: Request):
    return templates.TemplateResponse("busqueda.html", {"request": request})

@app.get("/estudios", response_class=HTMLResponse)
async def estudios(request: Request):
    return templates.TemplateResponse("estudios.html", {"request": request})

@app.get("/evolucion", response_class=HTMLResponse)
async def evolucion(request: Request):
    return templates.TemplateResponse("evolucion.html", {"request": request})

@app.get("/historia", response_class=HTMLResponse)
async def historia(request: Request):
    return templates.TemplateResponse("historia.html", {"request": request})

@app.get("/historia-clinica-completa", response_class=HTMLResponse)
async def historia_clinica_completa(request: Request):
    return templates.TemplateResponse("historia-clinica-completa.html", {"request": request})

@app.get("/historia-resumen", response_class=HTMLResponse)
async def historia_resumen(request: Request):
    return templates.TemplateResponse("historia-resumen.html", {"request": request})

@app.get("/indicaciones", response_class=HTMLResponse)
async def indicaciones(request: Request):
    return templates.TemplateResponse("indicaciones.html", {"request": request})

@app.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/receta", response_class=HTMLResponse)
async def receta(request: Request):
    return templates.TemplateResponse("receta.html", {"request": request})

@app.get("/registro", response_class=HTMLResponse)
async def registro(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})

@app.get("/turnos", response_class=HTMLResponse)
async def turnos(request: Request):
    return templates.TemplateResponse("turnos.html", {"request": request})

# ╔════════════════════════════════════╗
# ║       ARCHIVOS MÉDICOS            ║
# ╚════════════════════════════════════╝
@app.get("/listar-estudios")
async def listar_estudios():
    carpeta = "static/estudios"
    if os.path.exists(carpeta):
        return {"archivos": os.listdir(carpeta)}
    else:
        raise HTTPException(status_code=404, detail="Directorio no encontrado")

@app.post("/eliminar-estudio")
async def eliminar_estudio(nombre_archivo: str = Form(...)):
    ruta = f"static/estudios/{nombre_archivo}"
    if os.path.exists(ruta):
        os.remove(ruta)
        return {"status": "success", "message": "Archivo eliminado"}
    else:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

@app.get("/descargar-estudio/{nombre_archivo}")
async def descargar_estudio(nombre_archivo: str):
    ruta = f"static/estudios/{nombre_archivo}"
    if os.path.exists(ruta):
        return FileResponse(ruta, media_type="application/pdf", filename=nombre_archivo)
    else:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

@app.post("/subir-estudio")
async def subir_estudio(archivo: UploadFile = File(...)):
    extensiones_permitidas = [".pdf", ".jpg", ".jpeg", ".png"]
    extension = os.path.splitext(archivo.filename)[1].lower()
    if extension not in extensiones_permitidas:
        raise HTTPException(status_code=400, detail="Formato no permitido")
    ruta_guardado = f"static/estudios/{archivo.filename}"
    with open(ruta_guardado, "wb") as f:
        contenido = await archivo.read()
        f.write(contenido)
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
from admin_routes import router as admin_router
from acciones_pacientes import router as pacientes_router
from acciones_historia_clinica import router as historia_clinica_router
from routes import historia_resumen_router

app.include_router(admin_router)
app.include_router(pacientes_router)
app.include_router(historia_clinica_router)
