-- Tabla busqueda_pacientes vinculada al bucket 'busqueda-pacientes'
CREATE TABLE IF NOT EXISTS busqueda_pacientes (
    id serial PRIMARY KEY,
    dni text,
    nombres text,
    apellido text,
    telefono text,
    email text,
    fecha text,
    usuario_id text,
    pdf_url text NOT NULL,
    institucion_id text
);
