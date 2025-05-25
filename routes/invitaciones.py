from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/tarjeta-florencia", response_class=HTMLResponse)
async def tarjeta_florencia(request: Request):
    return templates.TemplateResponse("tarjeta_florencia.html", {"request": request})

@router.get("/confirmacion-florencia", response_class=HTMLResponse)
async def confirmacion_florencia(request: Request):
    return templates.TemplateResponse("confirmacion_florencia.html", {"request": request})
