-- Tabla turnos_medicos vinculada al bucket 'turnos-medicos'
CREATE TABLE IF NOT EXISTS turnos_medicos (
    id serial PRIMARY KEY,
    dni text,
    nombre text,
    apellido text,
    especialidad text,
    fecha date,
    horario time,
    profesional text,
    pdf_url text,
    institucion_id text
);
