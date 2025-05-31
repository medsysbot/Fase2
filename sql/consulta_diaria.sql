-- Tabla evolucion_diaria vinculada al bucket 'evolucion-diaria'
CREATE TABLE IF NOT EXISTS evolucion_diaria (
    dni text PRIMARY KEY,
    nombre text,
    apellido text,
    fecha date,
    diagnostico text,
    evolucion text,
    indicaciones text,
    institucion_id text
);
