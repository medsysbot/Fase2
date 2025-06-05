# 🤖 AGENTS.md - MedSys System Automation & Intelligent Agents

Este archivo documenta los agentes automatizados, asistentes y scripts inteligentes que intervienen en el ecosistema MedSys. Sigue un enfoque Agile, permitiendo que cada agente tenga una función clara, modular y evolutiva.

---

## 🧩 Estructura de Agentes

| Agente ID | Rol Principal                         | Activador                  | Descripción                                                       |
|-----------|----------------------------------------|----------------------------|-------------------------------------------------------------------|
| `AG-01`   | **Form Validator**                    | Frontend (`*.js`)          | Valida automáticamente formularios antes de enviarlos.            |
| `AG-02`   | **PDF Generator**                     | Backend (`/generar_pdf_`) | Genera PDFs desde formularios usando `WeasyPrint`.                |
| `AG-03`   | **Email Dispatcher**                  | Backend (`/enviar_pdf_`)  | Envía PDFs adjuntos a los correos de pacientes desde Supabase.   |
| `AG-04`   | **Voice Input Listener**              | `voz-a-formulario-*.js`   | Escucha comandos de voz y rellena campos automáticamente.         |
| `AG-05`   | **Supabase Sync Agent**               | Backend (`guardar_*.py`)  | Guarda datos validados en Supabase (tablas específicas por módulo).|
| `AG-06`   | **PDF Viewer Launcher**               | Frontend (`abrirPDF()`)   | Verifica y abre el PDF generado desde `sessionStorage.pdfURL`.    |
| `AG-07`   | **Alert Manager**                     | `alertas.js`              | Muestra alertas visuales coordinadas, con íconos personalizados.  |
| `AG-08`   | **Bucket File Manager**               | Backend (`supabase.storage`) | Gestiona firma, sello e imágenes en los buckets correctos.    |
| `AG-09`   | **SessionState Preloader**            | JS (`sessionStorage`)     | Precarga datos como `usuario_id`, `institucion_id`, `pdfURL`.     |
| `AG-10`   | **Error Fallback Logger**             | Global                    | Detecta errores y muestra alertas amigables en pantalla.          |

---

## 🛠️ Instrucciones para Nuevos Agentes

1. Define el `AG-XX` y su propósito.
2. Establece un único **activador claro** (frontend o backend).
3. Documenta cómo interactúa con otros agentes.
4. Añade su lógica en el sistema sin afectar la independencia de otros.

---

## 📌 Recomendaciones Agile

- Cada agente debe ser **modular**, **reutilizable** y tener una única responsabilidad.
- Evitar dependencia circular entre agentes.
- Todos los nuevos formularios deben conectarse automáticamente a los agentes necesarios.
- Las tareas de cada agente deben ser **trazables** y **documentadas en commits** con prefijo `[AG-XX]`.

---

## 📈 Visión a Futuro

MedSys usará esta arquitectura de agentes para:

- Orquestar flujos médicos en tiempo real.
- Integrar IA en tareas de seguimiento clínico.
- Implementar RPA (automatización robótica de procesos) para recepción, médicos y pacientes.

---

📁 Última revisión: mayo 2025  
✍️ Mantenedor: medisys.bot@gmail.com  
