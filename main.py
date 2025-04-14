from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import sqlite3
from utils import verificar_credenciales

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key='medsys-secret')
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Ruta SPLASH
@app.get("/", response_class=HTMLResponse)
async def splash(request: Request):
    return templates.TemplateResponse("splash_screen.html", {"request": request})

# --- Ruta LOGIN
@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    usuario: str = Form(...),
    contrasena: str = Form(...),
    rol: str = Form(...)
):
    if verificar_credenciales(usuario, contrasena, rol):
        request.session["usuario"] = usuario
        request.session["rol"] = rol
        return RedirectResponse(url="/index", status_code=302)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciales inválidas"})

# --- Ruta PRINCIPAL tras login
@app.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    if "usuario" not in request.session:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("index.html", {"request": request, "usuario": request.session["usuario"]})
