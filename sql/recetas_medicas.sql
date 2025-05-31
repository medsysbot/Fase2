-- Tabla recetas_medicas vinculada al bucket 'recetas-medicas'
CREATE TABLE IF NOT EXISTS recetas_medicas (
    dni text PRIMARY KEY,
    nombre text,
    apellido text,
    fecha date,
    diagnostico text,
    medicamentos text,
    pdf_url text,
    institucion_id text
);
