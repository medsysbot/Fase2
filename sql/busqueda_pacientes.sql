-- Tabla busqueda_pacientes vinculada al bucket 'busqueda-de-pacientes'
CREATE TABLE IF NOT EXISTS busqueda_pacientes (
    id serial PRIMARY KEY,
    busqueda text,
    institucion_id text
);
