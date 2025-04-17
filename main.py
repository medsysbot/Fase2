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
    print("Intentando login con:", usuario, contrasena, rol)
    try:
        conn = sqlite3.connect("static/doc/medsys.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombres, apellido FROM usuarios WHERE usuario=? AND contrasena=? AND rol=? AND activo=1", (usuario, contrasena, rol))
        user = cursor.fetchone()
        conn.close()
        print("Resultado de consulta SQL:", user)

        if user:
            request.session["usuario"] = usuario
            request.session["rol"] = rol
            request.session["nombres"] = user[0]
            request.session["apellido"] = user[1]
            print("Guardado en sesión:", request.session)
            return RedirectResponse(url="/splash-final", status_code=303)
        else:
            print("Login fallido")
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Usuario o contraseña incorrectos"
            })
    except Exception as e:
        print("ERROR EN LOGIN:", str(e))
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Error interno en el login"
        })

# ---------------- SPLASH FINAL ----------------
@app.get("/splash-final", response_class=HTMLResponse)
async def splash_final(request: Request):
    try:
        print("Entrando al splash-final")
        nombres = request.session.get("nombres", "")
        apellido = request.session.get("apellido", "")
        rol = request.session.get("rol", "")
        print("Desde sesión:", nombres, apellido, rol)

        if rol == "medico":
            titulo = "Doctora"
        elif rol == "secretaria":
            titulo = "Sra."
        else:
            titulo = ""

        print("Título asignado:", titulo)

        return templates.TemplateResponse("splash_final.html", {
            "request": request,
            "nombres": nombres,
            "apellido": apellido,
            "rol": rol,
            "titulo": titulo
        })

    except Exception as e:
        print("ERROR EN SPLASH:", str(e))
        return templates.TemplateResponse("error.html", {
            "request": request,
            "mensaje": f"Error al generar el splash: {str(e)}"
        })
