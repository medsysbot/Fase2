create table public.turnos_pacientes (
  id serial primary key,
  dni text not null,
  profesional text not null,
  especialidad text not null,
  fecha date not null,
  hora text not null,
  observaciones text,
  nombre text not null,
  apellido text not null,
  institucion_nombre text not null,
  pdf_url text,
  created_at timestamp without time zone default CURRENT_TIMESTAMP
);
