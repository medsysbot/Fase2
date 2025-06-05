# Rutas públicas de MedSys

Este documento detalla las rutas web de la parte pública (AppPublico) y los archivos que intervienen en cada una.

---

## Páginas

```
URL: /splash-turno-publico
Template: app_publico/templates/splash_turnos_publico.html
JS: (no aplica)
Python: routes/paginas.py (función `splash_turno_publico`)
```

```
URL: /solicitar-turno
Template: app_publico/templates/solicitar-turno-publico.html
JS: app_publico/static/js/turno_publico.js
Python: routes/paginas.py (función `ver_turno_publico`)
```

## APIs

```
API: /guardar_turno_publico → routes/acciones_turnos_pacientes_publico.py
API: /generar_pdf_turno_publico → routes/acciones_turnos_pacientes_publico.py
API: /enviar_pdf_turno_publico → routes/acciones_turnos_pacientes_publico.py
API: /obtener_email_paciente → routes/acciones_pacientes.py
```

Cada página utiliza el archivo `alertas.js` para mostrar mensajes en la interfaz. La plantilla de solicitud de turno carga también los íconos necesarios desde `/static/icons`.

---

Si alguna ruta no se encuentra operativa, revisar que `routes/paginas.py` esté incluido en `main.py` mediante `app.include_router(paginas_router)`.
