-- Tabla recetas_medicas vinculada al bucket 'recetas-medicas'
CREATE TABLE IF NOT EXISTS recetas_medicas (
    nombre text,
    dni text PRIMARY KEY,
    fecha date,
    diagnostico text,
    medicamentos text,
    profesional text,
    institucion_id text,
    pdf_url text,
    usuario_id text
);
