from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
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

# ---------------- Sesiones ----------------
app.add_middleware(SessionMiddleware, secret_key="clave-super-secreta")

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

# ---------------- LOGIN ----------------
@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(request: Request, usuario: str = Form(...), contrasena: str = Form(...), rol: str = Form(...)):
    conn = sqlite3.connect("static/doc/medsys.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND contrasena=? AND rol=? AND activo=1", (usuario, contrasena, rol))
    user = cursor.fetchone()
    conn.close()

    if user:
        request.session["usuario"] = usuario
        request.session["rol"] = rol
        request.session["nombres"] = user[3]
        request.session["apellido"] = user[4]
        return RedirectResponse(url="/splash-final", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Usuario o contrasena incorrectos"
        })

# ---------------- SPLASH FINAL ----------------
@app.get("/splash-final", response_class=HTMLResponse)
async def splash_final(request: Request):
    usuario_logueado = request.session.get("usuario")

    if not usuario_logueado:
        return templates.TemplateResponse("splash_final.html", {
            "request": request,
            "nombre": "Invitado",
            "titulo": ""
        })

    conn = sqlite3.connect("static/doc/medsys.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombres, apellido, rol FROM usuarios WHERE usuario=?", (usuario_logueado,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        nombres, apellido, rol = resultado
    else:
        nombres, apellido, rol = "Invitado", "", "desconocido"

    titulo = "Doctora" if rol in ["medico", "director"] else "Sra." if rol == "secretaria" else ""

    return templates.TemplateResponse("splash_final.html", {
        "request": request,
        "nombre": f"{nombres} {apellido}",
        "titulo": titulo
    })

# ---------------- RUTAS HTML ----------------
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

@app.get("/estudios", response_class=HTMLResponse)
async def estudios(request: Request):
    return templates.TemplateResponse("estudios.html", {"request": request})

# ---------------- ARCHIVOS MÉDICOS ----------------
@app.get("/listar-estudios")
async def listar_estudios():
    carpeta = "static/estudios"
    if os.path.exists(carpeta):
        return {"archivos": os.listdir(carpeta)}
    else:
        raise HTTPException(status_code=404, detail="Directorio de estudios no encontrado")

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
        raise HTTPException(status_code=400, detail="Formato de archivo no permitido")

    ruta_guardado = f"static/estudios/{archivo.filename}"
    with open(ruta_guardado, "wb") as f:
        contenido = await archivo.read()
        f.write(contenido)

    return {"status": "success", "message": "Archivo subido correctamente"}

# ---------------- RUTAS EXTERNAS ----------------
from admin_routes import router as admin_router
app.include_router(admin_router)

from acciones_pacientes import router as pacientes_router
app.include_router(pacientes_router)
