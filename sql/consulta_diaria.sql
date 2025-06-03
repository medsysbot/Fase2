-- Tabla consulta_diaria vinculada al bucket 'consulta-diaria'
CREATE TABLE IF NOT EXISTS consulta_diaria (
    id serial PRIMARY KEY,
    nombre text,
    apellido text,
    dni text,
    fecha date,
    diagnostico text,
    evolucion text,
    indicaciones text,
    institucion_id text,
    usuario_id text,
    pdf_url text,
    fecha_creacion timestamp
);
