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


@router.get("/usuarios/institucion")
async def usuarios_institucion(request: Request):
    if not validar_director(request):
        return JSONResponse({"error": "No autorizado"}, status_code=403)
    inst_id = request.session.get("institucion_id")
    res = (
        supabase.table("usuarios")
        .select("usuario,nombres,apellido,rol,institucion_id,activo")
        .eq("institucion_id", inst_id)
        .execute()
    )
    usuarios = []
    for u in res.data or []:
        inst = (
            supabase.table("instituciones")
            .select("nombre")
            .eq("id", u.get("institucion_id"))
            .single()
            .execute()
        )
        usuarios.append(
            {
                "usuario": u.get("usuario"),
                "nombres": u.get("nombres"),
                "apellido": u.get("apellido"),
                "rol": u.get("rol"),
                "institucion": inst.data.get("nombre") if inst.data else "",
                "activo": u.get("activo", False),
            }
        )
    return {"usuarios": usuarios}


@router.get("/pacientes/institucion")
async def pacientes_institucion(request: Request):
    if not validar_director(request):
        return JSONResponse({"error": "No autorizado"}, status_code=403)
    inst_id = request.session.get("institucion_id")
    res = (
        supabase.table("pacientes")
        .select("dni,nombres,apellido")
        .eq("institucion_id", inst_id)
        .execute()
    )
    return {"pacientes": res.data or []}


@router.get("/pacientes/descargar/{dni}")
async def descargar_paciente(request: Request, dni: str):
    if not validar_director(request):
        return JSONResponse({"error": "No autorizado"}, status_code=403)

    inst_id = request.session.get("institucion_id")
    pac = (
        supabase.table("pacientes")
        .select("*")
        .eq("dni", dni)
        .eq("institucion_id", inst_id)
        .single()
        .execute()
    )
    if not pac.data:
        return JSONResponse({"error": "Paciente no encontrado"}, status_code=404)

    import tempfile, zipfile

    buckets = [
        "registro-pacientes",
        "historia-completa",
        "historia-clinica-resumida",
        "recetas-medicas",
        "indicaciones-medicas",
        "consulta-diaria",
        "estudios-medicos",
    ]

    tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    with zipfile.ZipFile(tmp_zip.name, "w") as zipf:
        # agregar datos del paciente
        info_txt = "\n".join(f"{k}: {v}" for k, v in pac.data.items())
        zipf.writestr("datos_paciente.txt", info_txt)

        for bucket in buckets:
            try:
                archivos = supabase.storage.from_(bucket).list()
                for a in archivos:
                    nombre = a.get("name")
                    if nombre and nombre.startswith(str(dni)):
                        contenido = supabase.storage.from_(bucket).download(nombre)
                        zipf.writestr(f"{bucket}/{nombre}", contenido)
            except Exception:
                pass

    return FileResponse(tmp_zip.name, filename=f"paciente_{dni}.zip")




@router.delete("/usuarios/eliminar")
async def eliminar_usuario(request: Request):
    if not validar_director(request):
        return JSONResponse({"error": "No autorizado"}, status_code=403)
    datos = await request.json()
    usuario = datos.get("usuario")
    supabase.table("usuarios").delete().eq("usuario", usuario).execute()
    return {"exito": True}


@router.post("/usuarios/agregar")
async def agregar_usuario(request: Request):
    if not validar_director(request):
        return JSONResponse({"error": "No autorizado"}, status_code=403)
    datos = await request.json()
    nuevo = {
        "usuario": datos.get("usuario"),
        "contrasena": datos.get("contrasena"),
        "nombres": datos.get("nombres"),
        "apellido": datos.get("apellido"),
        "rol": datos.get("rol"),
        "institucion_id": datos.get("institucion"),
        "activo": True,
    }
    supabase.table("usuarios").insert(nuevo).execute()
    return {"exito": True}


@router.put("/usuarios/estado")
async def cambiar_estado_usuario(request: Request):
    if not validar_director(request):
        return JSONResponse({"error": "No autorizado"}, status_code=403)
    datos = await request.json()
    usuario = datos.get("usuario")
    activo = datos.get("activo", True)
    supabase.table("usuarios").update({"activo": activo}).eq("usuario", usuario).execute()
    return {"exito": True}
