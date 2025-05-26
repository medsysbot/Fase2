import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno una sola vez
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def get_supabase_client() -> Client:
    """Devuelve una instancia del cliente de Supabase."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise EnvironmentError(
            "Variables SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY no definidas. "
            "Revise el archivo .env.example"
        )
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        raise RuntimeError(f"Error al crear cliente de Supabase: {e}")


# Cliente reutilizable en toda la aplicación
supabase: Client = get_supabase_client()
