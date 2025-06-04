# Referencia de Formularios y Conexiones

Esta tabla resume qué archivos HTML usan cada JavaScript, qué rutas del backend (en `routes/`) procesan sus datos y en qué tabla de Supabase se guardan.

| Formulario HTML | JavaScript asociado | Ruta Python | Tabla Supabase |
|-----------------|--------------------|-------------|---------------|
| registro-pacientes.html | alertas.js, registro_pacientes.js | acciones_registro_pacientes.py | registro_pacientes |
| busqueda_pacientes.html | guardar_busqueda.js, voz-a-formulario-busqueda.js, alertas.js | acciones_busqueda.py | busqueda_pacientes |
| consulta-diaria.html | consulta_diaria.js, voz-a-formulario-consulta-diaria.js, alertas.js | acciones_consulta_diaria.py | consulta_diaria |
| recetas-medicas.html | recetas_medicas.js, voz-a-formulario-recetas_medicas.js, alertas.js | acciones_recetas_medicas.py | recetas_medicas |
| historia-clinica-completa.html | historia_clinica_completa.js, voz-a-formulario-historia_clinica_completa.js, alertas.js | acciones_historia_clinica_completa.py | historia_clinica_completa |
| historia-clinica-resumida.html | historia_clinica_resumida.js, voz-a-formulario-historia_clinica_resumida.js, alertas.js | acciones_historia_clinica_resumida.py | historia_clinica_resumida |
| indicaciones-medicas.html | indicaciones_medicas.js, voz-a-formulario-indicaciones_medicas.js, alertas.js | acciones_indicaciones_medicas.py | indicaciones_medicas |
| enfermeria.html | enfermeria.js, voz-a-formulario-enfermeria.js, alertas.js | acciones_enfermeria.py | enfermeria |
| estudios-medicos.html | estudios_medicos.js, alertas.js | acciones_estudios.py | estudios |
| solicitar-turno-publico.html | turno_publico.js, alertas.js | acciones_turnos_pacientes_publico.py | turnos_pacientes |
| firma_sello.html | firma_sello.js, subir_firma_sello.js | acciones_recetas_medicas.py | (usa bucket "firma-sello-usuarios") |

Notas:
- Algunos formularios usan archivos de voz (`voz-a-formulario-*.js`) para dictado por voz.
