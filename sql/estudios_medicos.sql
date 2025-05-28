-- Tabla estudios_medicos vinculada al bucket 'estudios-medicos'
CREATE TABLE IF NOT EXISTS estudios_medicos (
    paciente_id text PRIMARY KEY,
    nombre text,
    apellido text,
    tipo_estudio text,
    pdf_url text,
    institucion_id text
);
