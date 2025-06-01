-- Tabla busqueda_pacientes vinculada al bucket 'busqueda-de-pacientes'
CREATE TABLE IF NOT EXISTS busqueda_pacientes (
    id serial PRIMARY KEY,
    dni text,
    nombres text,
    apellido text,
    telefono text,
    email text,
    institucion_id text
);
