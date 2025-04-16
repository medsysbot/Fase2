
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3

router = APIRouter()
templates = Jinja2Templates(directory="templates")
DB_PATH = "static/doc/medsys.db"

@router.get("/admin/db-inspect", response_class=HTMLResponse)
async def db_inspect(request: Request, tabla: str = None):
    tablas = []
    columnas = []
    registros = []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas = [fila[0] for fila in cursor.fetchall()]

    if tabla:
        try:
            cursor.execute(f"PRAGMA table_info({tabla})")
            columnas = [col[1] for col in cursor.fetchall()]
            cursor.execute(f"SELECT * FROM {tabla} LIMIT 50")
            registros = cursor.fetchall()
        except Exception as e:
            columnas = ["Error"]
            registros = [(str(e),)]

    conn.close()

    return templates.TemplateResponse("db_inspector.html", {
        "request": request,
        "tablas": tablas,
        "tabla_actual": tabla,
        "columnas": columnas,
        "registros": registros
    })
