-- Tabla historia_completa vinculada al bucket 'historia-completa'
CREATE TABLE IF NOT EXISTS historia_completa (
    dni text PRIMARY KEY,
    nombre text,
    apellido text,
    fecha_nacimiento date,
    edad text,
    sexo text,
    domicilio text,
    telefono text,
    obra_social text,
    numero_afiliado text,
    antecedentes_personales text,
    antecedentes_familiares text,
    habitos text,
    enfermedades_cronicas text,
    cirugias text,
    medicacion text,
    estudios text,
    historial_tratamientos text,
    historial_consultas text,
    institucion_id text
);
