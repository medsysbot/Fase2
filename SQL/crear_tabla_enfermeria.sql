-- Tabla datos_enfermeria para formulario de enfermería
CREATE TABLE IF NOT EXISTS datos_enfermeria (
    dni text PRIMARY KEY,
    institucion_id text,
    usuario_id text,
    profesional text,
    motivo_consulta text,
    hora time,
    temperatura numeric,
    saturacion numeric,
    ta numeric,
    tad numeric,
    frecuencia_cardiaca numeric,
    glasgow int,
    dolor int,
    glucemia numeric,
    triaje text
);
