from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ══════════════════════════════════════════════════════════
# MODULOS A TESTEAR
# ══════════════════════════════════════════════════════════
modulos = [
    ("registro_pacientes", "registro-pacientes"),
    ("historia_clinica_completa", "historia-clinica-completa"),
    ("historia_clinica_resumida", "historia-clinica-resumida"),
    ("consulta_diaria", "consulta-diaria"),
    ("indicaciones_medicas", "indicaciones-medicas"),
    ("recetas_medicas", "recetas-medicas"),
    ("turnos_pacientes", "turnos-pacientes")
]

# ══════════════════════════════════════════════════════════
# FUNCIONES
# ══════════════════════════════════════════════════════════
def test_tabla(tabla):
    print(f"\n\ud83d\udd0d Verificando tabla: {tabla}")
    try:
        res = supabase.table(tabla).select("*").limit(1).execute()
        if res.data:
            print("\u2705 Conexi\xf3n OK.")
            row = res.data[0]
            campos = row.keys()
            print(f"\ud83d\udd11 Campos detectados: {list(campos)}")

            if "usuario_id" in campos:
                print("\u2714 campo 'usuario_id' OK")
            else:
                print("\u274c campo 'usuario_id' NO encontrado")

            if "institucion_id" in campos:
                print("\u2714 campo 'institucion_id' OK")
            else:
                print("\u274c campo 'institucion_id' NO encontrado")
        else:
            print("\u26a0\ufe0f  Tabla vac\xeda, no se puede validar campos.")
    except Exception as e:
        print(f"\u274c ERROR al acceder a {tabla}: {e}")

def test_bucket(bucket):
    print(f"\ud83e\udea3 Verificando bucket: {bucket}")
    try:
        archivos = supabase.storage.from_(bucket).list()
        print(f"\u2705 Bucket activo. Archivos: {len(archivos)}")
    except Exception as e:
        print(f"\u274c ERROR al acceder a bucket {bucket}: {e}")


# ══════════════════════════════════════════════════════════
# EJECUCIÓN
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\ud83d\udce6 INICIANDO DIAGN\xd3STICO COMPLETO DE MEDSYS")

    for tabla, bucket in modulos:
        test_tabla(tabla)
        test_bucket(bucket)

    print("\n\u2705 Diagn\xf3stico finalizado.")
