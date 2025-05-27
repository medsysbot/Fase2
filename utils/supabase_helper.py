import os
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno una sola vez
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


class DummySupabase:
    """Cliente de respaldo cuando la configuración de Supabase es inválida."""

    def __getattr__(self, name):
        def _missing(*args, **kwargs):
            raise RuntimeError(
                "Supabase no configurado correctamente. "
                "Verifique su archivo .env"
            )

        return _missing


def get_supabase_client() -> Client:
    """Devuelve una instancia del cliente de Supabase o un dummy si falla."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        logging.warning(
            "Variables SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY no definidas"
        )
        return DummySupabase()
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logging.error(f"Error al crear cliente de Supabase: {e}")
        return DummySupabase()


# Cliente reutilizable en toda la aplicación
supabase: Client = get_supabase_client()


def subir_pdf(bucket: str, nombre: str, datos) -> str:
    """Sube un PDF al bucket indicado y devuelve su URL pública."""
    opciones = {"content-type": "application/pdf", "x-upsert": "true"}
    supabase.storage.from_(bucket).upload(nombre, datos, opciones)
    url_obj = supabase.storage.from_(bucket).get_public_url(nombre)
    return url_obj.get("publicUrl") if isinstance(url_obj, dict) else url_obj
