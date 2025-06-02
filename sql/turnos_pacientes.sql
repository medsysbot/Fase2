-- Tabla turnos_pacientes vinculada al bucket 'turnos-pacientes'
CREATE TABLE IF NOT EXISTS turnos_pacientes (
    id serial PRIMARY KEY,
    dni text,
    nombre text,
    apellido text,
    especialidad text,
    fecha date,
    hora time,
    profesional text,
    observaciones text,
    pdf_url text,
    institucion_id text,
    usuario_id text
);
