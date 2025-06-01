import importlib.util
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.supabase_helper import (
    SUPABASE_URL,
    SUPABASE_KEY,
    check_supabase_connection,
)

REQUIRED_LIBS = [
    'fastapi', 'uvicorn', 'fpdf', 'jinja2', 'python-multipart', 'pydantic',
    'itsdangerous', 'supabase', 'python-dotenv', 'requests',
    'psycopg2', 'asyncpg', 'httpx'
]

REQUIRED_ENV_VARS = [
    'SUPABASE_URL',
    'SUPABASE_SERVICE_ROLE_KEY',
    'SUPABASE_KEY',
    'DATABASE_URL',
    'EMAIL_ORIGEN',
    'EMAIL_PASSWORD',
]


def check_libraries():
    missing = []
    for lib in REQUIRED_LIBS:
        if importlib.util.find_spec(lib) is None:
            missing.append(lib)
    return missing


def check_env_variables():
    """Return a list of required environment variables that are missing."""
    missing = []
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing.append(var)
    return missing


def run_checks():
    print('SUPABASE_URL definido:', bool(SUPABASE_URL))
    print('SUPABASE_KEY definido:', bool(SUPABASE_KEY))
    if SUPABASE_URL and not SUPABASE_URL.startswith('http'):
        print('Advertencia: SUPABASE_URL parece inválido ->', SUPABASE_URL)

    env_missing = check_env_variables()
    if env_missing:
        print('Variables de entorno faltantes:', ', '.join(env_missing))

    print('Conexión a Supabase:', 'ok' if check_supabase_connection() else 'falló')

    missing = check_libraries()
    if missing:
        print('Faltan librerías:', ', '.join(missing))
        print('Sugerencia: ejecutar "pip install -r requirements.txt"')
    else:
        print('Todas las librerías requeridas están instaladas.')


if __name__ == '__main__':
    run_checks()
