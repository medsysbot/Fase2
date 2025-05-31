from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()


def _session_activa(request: Request) -> bool:
    """Verifica si existe una sesión de usuario activa."""
    return request.session.get("usuario") is not None


@router.get("/index", response_class=HTMLResponse)
async def ver_index(request: Request):
    rol = request.session.get("rol")
    if not rol:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request, "rol": rol})


@router.get("/registro", response_class=HTMLResponse)
async def ver_registro(request: Request):
    if not _session_activa(request):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("registro.html", {"request": request})


@router.get("/consulta_diaria", response_class=HTMLResponse)
async def ver_consulta_diaria(request: Request):
    if not _session_activa(request):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("consulta_diaria.html", {"request": request})


@router.get("/receta", response_class=HTMLResponse)
async def ver_receta(request: Request):
    if not _session_activa(request):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("receta.html", {"request": request})


@router.get("/historia", response_class=HTMLResponse)
async def ver_historia(request: Request):
    if not _session_activa(request):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("historia.html", {"request": request})


@router.get("/indicaciones", response_class=HTMLResponse)
async def ver_indicaciones(request: Request):
    if not _session_activa(request):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("indicaciones.html", {"request": request})


@router.get("/turnos", response_class=HTMLResponse)
async def ver_turnos(request: Request):
    if not _session_activa(request):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("turnos.html", {"request": request})


@router.get("/enfermeria", response_class=HTMLResponse)
async def ver_enfermeria(request: Request):
    if not _session_activa(request):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("enfermeria.html", {"request": request})


@router.get("/busqueda", response_class=HTMLResponse)
async def ver_busqueda(request: Request):
    if not _session_activa(request):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("busqueda.html", {"request": request})


@router.get("/estudios", response_class=HTMLResponse)
async def ver_estudios(request: Request):
    if not _session_activa(request):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("estudios-medicos.html", {"request": request})

@router.get("/estudios-medicos", response_class=HTMLResponse)
async def ver_estudios_alias(request: Request):
    if not _session_activa(request):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("estudios-medicos.html", {"request": request})


@router.get("/firma-sello", response_class=HTMLResponse)
async def ver_firma_sello(request: Request):
    if not _session_activa(request):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("firma_sello.html", {"request": request})


@router.get("/historia_clinica_resumida", response_class=HTMLResponse)
async def ver_historia_clinica_resumida(request: Request):
    if not _session_activa(request):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("historia_clinica_resumida.html", {"request": request})


@router.get("/historia-clinica-completa", response_class=HTMLResponse)
async def ver_historia_completa(request: Request):
    if not _session_activa(request):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("historia-clinica-completa.html", {"request": request})


@router.get("/solicitar-turno", response_class=HTMLResponse)
async def ver_turno_publico(request: Request):
    """Portal público para solicitar turnos."""
    return templates.TemplateResponse(
        "app_publico/splash_turno_publico.html",
        {"request": request},
    )
