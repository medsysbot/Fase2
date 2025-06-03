-- Tabla historia_clinica_resumida vinculada al bucket 'historia-clinica-resumida'
CREATE TABLE IF NOT EXISTS historia_clinica_resumida (
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
