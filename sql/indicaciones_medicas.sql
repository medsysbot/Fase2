-- Tabla indicaciones_medicas vinculada al bucket 'indicaciones-medicas'
CREATE TABLE IF NOT EXISTS indicaciones_medicas (
    dni text PRIMARY KEY,
    nombre text,
    apellido text,
    fecha date,
    diagnostico text,
    indicaciones text,
    institucion_id text
);
