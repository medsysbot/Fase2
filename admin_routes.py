@router.get("/admin/pacientes", response_class=HTMLResponse)
async def admin_pacientes(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Instituciones
    cursor.execute("SELECT id, nombre, estado FROM instituciones")
    instituciones_raw = cursor.fetchall()
    instituciones = []
    for inst in instituciones_raw:
        cursor.execute("SELECT COUNT(*) FROM pacientes WHERE institucion=?", (inst[0],))
        total = cursor.fetchone()[0]
        instituciones.append({
            "id": inst[0],
            "nombre": inst[1],
            "estado": inst[2],
            "total": total
        })

    # Usuarios
    cursor.execute("SELECT usuario, rol, institucion, activo FROM usuarios")
    usuarios_raw = cursor.fetchall()
    usuarios = []
    for u in usuarios_raw:
        usuarios.append({
            "usuario": u[0],
            "rol": u[1],
            "institucion": u[2],
            "activo": u[3]
        })

    # Pacientes
    cursor.execute("SELECT id, nombre, apellido, dni, institucion, telefono, email FROM pacientes")
    pacientes = cursor.fetchall()

    conn.close()

    return templates.TemplateResponse("admin-pacientes.html", {
        "request": request,
        "instituciones": instituciones,
        "usuarios": usuarios,
        "pacientes": pacientes
    })
