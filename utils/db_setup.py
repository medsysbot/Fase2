import logging
from dotenv import load_dotenv
import psycopg2
from .supabase_helper import get_db_connection


def prepare_consultas_table():
    """Asegura que la tabla 'consultas' tenga las columnas necesarias
    y que el campo dni no posea restricciones de unicidad."""
    load_dotenv()

    try:
        conn = get_db_connection()
    except psycopg2.OperationalError as e:
        logging.error(f"No se pudo conectar a la base de datos: {e}")
        return

    cur = conn.cursor()

    try:
        # Agregar columnas si no existen y clave primaria id
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
