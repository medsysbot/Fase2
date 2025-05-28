-- Tabla historia_resumen vinculada al bucket 'historia-resumen'
CREATE TABLE IF NOT EXISTS historia_resumen (
    dni text PRIMARY KEY,
    nombre text,
    apellido text,
    edad text,
    motivo text,
    diagnostico text,
    tratamiento text,
    observaciones text,
    institucion_id text
);
