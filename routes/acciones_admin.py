from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from utils.supabase_helper import supabase

router = APIRouter(prefix="/api")


def validar_director(request: Request):
    usuario = request.session.get("usuario")
    rol = request.session.get("rol")
    if not usuario or rol != "director":
        return False
    return True


@router.get("/instituciones/listar")
async def listar_instituciones(request: Request):
    if not validar_director(request):
        return JSONResponse({"error": "No autorizado"}, status_code=403)
    res = supabase.table("instituciones").select("id,nombre,estado").execute()
    instituciones = []
    for inst in res.data or []:
        pid = inst.get("id")
        total_pacientes = supabase.table("pacientes").select("id", count="exact").eq("institucion_id", pid).execute()
        total_usuarios = supabase.table("usuarios").select("id", count="exact").eq("institucion_id", pid).execute()
        instituciones.append({
            "id": pid,
            "nombre": inst.get("nombre"),
            "estado": inst.get("estado", ""),
            "total_pacientes": total_pacientes.count or 0,
            "total_usuarios": total_usuarios.count or 0,
        })
    return {"instituciones": instituciones}


@router.get("/usuarios/listar")
async def listar_usuarios(request: Request):
    if not validar_director(request):
        return JSONResponse({"error": "No autorizado"}, status_code=403)
    res = supabase.table("usuarios").select("usuario,nombres,apellido,rol,institucion_id,activo").execute()
    usuarios = []
    for u in res.data or []:
        inst = supabase.table("instituciones").select("nombre").eq("id", u.get("institucion_id")).single().execute()
        usuarios.append({
            "usuario": u.get("usuario"),
            "nombres": u.get("nombres"),
            "apellido": u.get("apellido"),
            "rol": u.get("rol"),
            "institucion": inst.data.get("nombre") if inst.data else "",
            "activo": u.get("activo", False),
        })
    return {"usuarios": usuarios}


@router.post("/instituciones/activar")
async def activar_institucion(request: Request):
    if not validar_director(request):
        return JSONResponse({"error": "No autorizado"}, status_code=403)
    datos = await request.json()
    id_inst = datos.get("id")
    supabase.table("instituciones").update({"estado": "activa"}).eq("id", id_inst).execute()
    return {"exito": True}


@router.post("/instituciones/pausar")
async def pausar_institucion(request: Request):
    if not validar_director(request):
        return JSONResponse({"error": "No autorizado"}, status_code=403)
    datos = await request.json()
    id_inst = datos.get("id")
    supabase.table("instituciones").update({"estado": "pausada"}).eq("id", id_inst).execute()
    return {"exito": True}


@router.delete("/instituciones/eliminar")
async def eliminar_institucion(request: Request):
    if not validar_director(request):
        return JSONResponse({"error": "No autorizado"}, status_code=403)
    datos = await request.json()
    id_inst = datos.get("id")
    supabase.table("instituciones").delete().eq("id", id_inst).execute()
    return {"exito": True}


@router.delete("/usuarios/eliminar")
async def eliminar_usuario(request: Request):
    if not validar_director(request):
        return JSONResponse({"error": "No autorizado"}, status_code=403)
    datos = await request.json()
    usuario = datos.get("usuario")
    supabase.table("usuarios").delete().eq("usuario", usuario).execute()
    return {"exito": True}
