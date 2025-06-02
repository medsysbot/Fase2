create table public.turnos_pacientes (
  id serial primary key,
  dni text not null,
  institucion_id integer not null,
  usuario_id text not null,
  profesional text not null,
  especialidad text not null,
  fecha date not null,
  hora text not null,
  observaciones text,
  nombre text not null,
  apellido text not null,
  pdf_url text,
  created_at timestamp without time zone default CURRENT_TIMESTAMP,
  constraint turnos_pacientes_institucion_id_fkey foreign key (institucion_id) references instituciones (id) on delete cascade
);
