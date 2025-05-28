-- Tabla turnos_medicos vinculada al bucket 'turnos-medicos'
CREATE TABLE IF NOT EXISTS turnos_medicos (
    dni text PRIMARY KEY,
    nombre text,
    apellido text,
    especialidad text,
    fecha date,
    horario time,
    profesional text,
    institucion_id text
);
