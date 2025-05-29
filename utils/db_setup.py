import logging
from dotenv import load_dotenv
import psycopg2
from .supabase_helper import get_db_connection


def prepare_consultas_table():
    """Asegura que exista la tabla ``consultas`` y que contenga las
    columnas necesarias. También elimina cualquier restricción de
    unicidad sobre ``dni`` que pueda impedir registrar múltiples
    evoluciones para un mismo paciente."""
    load_dotenv()

    try:
        conn = get_db_connection()
    except psycopg2.OperationalError as e:
        logging.error(f"No se pudo conectar a la base de datos: {e}")
        return

    cur = conn.cursor()

    try:
        # Crear la tabla si no existe con las columnas básicas
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS consultas (
                id SERIAL PRIMARY KEY,
                paciente TEXT,
                dni TEXT,
                fecha TEXT,
                diagnostico TEXT,
                evolucion TEXT,
                indicaciones TEXT,
                usuario_id TEXT,
                institucion_id TEXT,
                firma_url TEXT,
                sello_url TEXT,
                pdf_url TEXT
            );
            """
        )

        # Agregar columnas que puedan faltar (id, firma_url, sello_url)
        cur.execute(
            """
            ALTER TABLE IF EXISTS consultas
                ADD COLUMN IF NOT EXISTS id SERIAL PRIMARY KEY,
                ADD COLUMN IF NOT EXISTS firma_url TEXT,
                ADD COLUMN IF NOT EXISTS sello_url TEXT;
            """
        )

        # Eliminar posibles restricciones de unicidad sobre dni
        cur.execute(
            """
            DO $$
            DECLARE
                c RECORD;
            BEGIN
                FOR c IN SELECT conname FROM pg_constraint
                    WHERE conrelid = 'consultas'::regclass AND contype IN ('u', 'p') LOOP
                    IF position('dni' IN pg_get_constraintdef(c.oid)) > 0 THEN
                        EXECUTE format('ALTER TABLE consultas DROP CONSTRAINT %I', c.conname);
                    END IF;
                END LOOP;
            END$$;
            """
        )

        conn.commit()
    finally:
        cur.close()
        conn.close()
