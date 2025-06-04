-- Tabla registro_pacientes vinculada al bucket 'registro-pacientes'
CREATE TABLE IF NOT EXISTS registro_pacientes (
    dni text PRIMARY KEY,
    nombres text,
    apellido text,
    fecha_nacimiento date,
    telefono text,
    email text,
    domicilio text,
    obra_social text,
    numero_afiliado text,
    contacto_emergencia text,
    usuario_id text,
    institucion_id int4,
    pdf_url text
);
