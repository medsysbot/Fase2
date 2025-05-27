import os
import psycopg2


def prepare_consultas_table():
    """Asegura que la tabla 'consultas' tenga las columnas necesarias
    y que el campo dni no posea restricciones de unicidad."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Sin cadena de conexión no podemos aplicar cambios
        return

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

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
    cur.close()
    conn.close()
