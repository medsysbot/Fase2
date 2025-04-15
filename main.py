from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
import os

from admin_routes import router as admin_router

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Archivos Estáticos ----------------
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- Templates ----------------
templates = Jinja2Templates(directory="templates")

# ---------------- Ruta SPLASH INICIAL ----------------
@app.get("/", response_class=HTMLResponse)
async def splash_inicio(request: Request):
    return templates.TemplateResponse("splash_screen.html", {"request": request})

# ---------------- SPLASH FINAL ----------------
@app.get("/splash-final", response_class=HTMLResponse)
async def splash_final(request: Request):
    return templates.TemplateResponse("splash_final.html", {"request": request})

# ---------------- LOGIN (GET) ----------------
@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# ---------------- LOGIN (POST) ----------------
@app.post("/login")
async def login_post(request: Request, usuario: str = Form(...), contrasena: str = Form(...), rol: str = Form(...)):
    conn = sqlite3.connect("static/doc/medsys.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND contrasena=? AND rol=? AND activo=1", (usuario, contrasena, rol))
    user = cursor.fetchone()
    conn.close()
    if user:
        return RedirectResponse(url="/splash-final", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Usuario o contraseña incorrectos"})

# ---------------- RUTA PRINCIPAL INDEX ----------------
@app.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ---------------- INCLUIR PANEL SUPERADMIN ----------------
app.include_router(admin_router)
