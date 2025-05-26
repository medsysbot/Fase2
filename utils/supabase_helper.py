import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno una sola vez
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def get_supabase_client() -> Client:
    """Devuelve una instancia del cliente de Supabase."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# Cliente reutilizable en toda la aplicación
supabase: Client = get_supabase_client()
