import importlib.util
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.supabase_helper import SUPABASE_URL, SUPABASE_KEY, check_supabase_connection

REQUIRED_LIBS = [
    'fastapi', 'uvicorn', 'fpdf', 'jinja2', 'python-multipart', 'pydantic',
    'itsdangerous', 'supabase', 'python-dotenv', 'requests',
    'psycopg2', 'asyncpg', 'httpx'
]


def check_libraries():
    missing = []
    for lib in REQUIRED_LIBS:
        if importlib.util.find_spec(lib) is None:
            missing.append(lib)
    return missing


def run_checks():
    print('SUPABASE_URL definido:', bool(SUPABASE_URL))
    print('SUPABASE_KEY definido:', bool(SUPABASE_KEY))
    print('Conexión a Supabase:', 'ok' if check_supabase_connection() else 'falló')
    missing = check_libraries()
    if missing:
        print('Faltan librerías:', ', '.join(missing))
    else:
        print('Todas las librerías requeridas están instaladas.')


if __name__ == '__main__':
    run_checks()
