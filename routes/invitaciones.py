from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/tarjeta-marialuz", response_class=HTMLResponse)
async def tarjeta_marialuz(request: Request):
    return templates.TemplateResponse("tarjeta_marialuz.html", {"request": request})

