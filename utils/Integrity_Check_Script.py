
from supabase import create_client
import os

# ╔═════════════════════════════════════════════════════════════════════╗
# ║        VERIFICADOR DE CAMPOS: pdf_url, firma_url, sello_url        ║
# ╚═════════════════════════════════════════════════════════════════════╝

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("⚠️ SUPABASE_URL o SUPABASE_KEY no están definidas.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def revisar_campos(tabla, campos):
    print(f"🔎 Revisando tabla: {tabla}")
    resultados = supabase.table(tabla).select("*").limit(10).execute()
    for fila in resultados.data:
        errores = []
        for campo in campos:
            if not fila.get(campo):
                errores.append(f"❌ FALTA {campo}")
        if errores:
            print(f"DNI {fila.get('dni', 'sin_dni')} → {' | '.join(errores)}")
        else:
            print(f"✅ OK - Todos los campos presentes")
    print("")

# Definir qué campos verificar por tabla
tablas_a_verificar = {
    "historia_clinica_completa": ["pdf_url", "firma_url", "sello_url"],
    "historia_clinica_resumida": ["pdf_url", "firma_url", "sello_url"],
    "indicaciones": ["pdf_url", "firma_url", "sello_url"],
    "recetas": ["pdf_url", "firma_url", "sello_url"],
    "consulta_diaria": ["pdf_url", "firma_url", "sello_url"],
    "busqueda_pacientes": ["pdf_url"],
    "turnos_pacientes": [],  # no genera PDF ni firma/sello
    "pacientes": [],         # solo registro, sin PDF
}

for tabla, campos in tablas_a_verificar.items():
    if campos:
        revisar_campos(tabla, campos)
