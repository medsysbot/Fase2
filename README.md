# Backend Fase 2 MEDSYS  
**Versión estable con carpeta `static/` incluida**

---

## RITMIC – Deploy Railway Instantáneo Totalmente Modular, Inteligente y Consistente

---

### PASOS PARA DESPLEGAR EN RAILWAY

1. **Subí el ZIP** ya corregido:  
   `backend_fase2_corregido_con_static.zip`

2. Railway detecta automáticamente:
   - Lenguaje: **Python**
   - Framework: **FastAPI**
   - Archivo principal: `main.py`
   - Procfile:  
     ```
     web: uvicorn main:app --host=0.0.0.0 --port=${PORT}
     ```

3. Si no lo detecta, configurá manualmente:
   - **Start Command**:
     ```
     uvicorn main:app --host=0.0.0.0 --port=${PORT}
     ```

4. **Variables de entorno:**
   Copiá el archivo `.env.example` a `.env` y completá tus valores de
   `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `EMAIL_ORIGEN`,
   `EMAIL_PASSWORD`, `SMTP_SERVER` y `SMTP_PORT`.
5. Una vez desplegado, podés testear las rutas:

   #### `GET /`
   Respuesta esperada:
   ```json
   { "status": "OK" }
   ```

   #### `POST /generate`
   Enviá un JSON como este:
   ```json
   {
     "patient_name": "Juan Pérez",
     "diagnosis": "Hipertensión arterial",
     "notes": "Paciente estable. Controlar en 15 días."
   }
   ```
   Respuesta esperada:
   ```json
   {
     "pdf": "https://<tu-app>.railway.app/static/Juan_Perez.pdf"
   }
   ```

---

### NOTAS IMPORTANTES

- La carpeta `/static` **ya viene incluida**. Si se elimina, el backend crashea.
- Los PDFs generados se guardan automáticamente ahí.
- Esta versión es estable, funcional, y lista para seguir con la Fase 2B (firmas, QR, recetas).
