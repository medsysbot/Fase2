from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/tester")


def _session_activa(request: Request) -> bool:
    return request.session.get("usuario") is not None


@router.get("/", response_class=HTMLResponse)
async def ver_tester(request: Request):
    if not _session_activa(request):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("tester.html", {"request": request})


@router.get("/estado")
async def estado_sesion(request: Request):
    if not _session_activa(request):
        return JSONResponse({"activa": False}, status_code=401)
    return {"activa": True}
