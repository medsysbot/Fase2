from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
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

# ---------------- Splash inicial ----------------
@app.get("/", response_class=HTMLResponse)
async def root_redirect(request: Request):
    return templates.TemplateResponse("splash_screen.html", {"request": request})

# ---------------- LOGIN ----------------
@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(request: Request, usuario: str = Form(...), contrasena: str = Form(...), rol: str = Form(...)):
    conn = sqlite3.connect("static/doc/medsys.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombres, apellido FROM usuarios WHERE usuario=? AND contrasena=? AND rol=? AND activo=1", (usuario, contrasena, rol))
    user = cursor.fetchone()
    conn.close()

    if user:
        request.session["usuario"] = usuario
        request.session["rol"] = rol
        request.session["nombres"] = user[0]
        request.session["apellido"] = user[1]
        return RedirectResponse(url="/splash-final", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Usuario o contraseña incorrectos"
        })

# ---------------- SPLASH FINAL ----------------
@app.get("/splash-final", response_class=HTMLResponse)
async def splash_final(request: Request):
    try:
        nombres = request.session.get("nombres", "")
        apellido = request.session.get("apellido", "")
        rol = request.session.get("rol", "")

        if rol == "medico":
            titulo = "Doctora"
        elif rol == "secretaria":
            titulo = "Sra."
        else:
            titulo = ""

        return templates.TemplateResponse("splash_final.html", {
            "request": request,
            "nombres": nombres,
            "apellido": apellido,
            "rol": rol,
            "titulo": titulo
        })

    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "mensaje": f"Error al generar el splash: {str(e)}"
        })
