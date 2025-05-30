document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('form-turnos');
  // Busca el botón "Enviar" por su tipo, así no dependés de IDs
  const enviarBtn = form ? form.querySelector('button[type="submit"]') : null;

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (enviarBtn) {
        enviarBtn.disabled = true;
      }

      // Arma el FormData con todos los campos del formulario
      const formData = new FormData(form);

      try {
        const response = await fetch('/solicitar_turno_publico', {
          method: 'POST',
          body: formData
        });

        const data = await response.json();

        if (data.exito) {
          showAlert({
            mensaje: "¡Turno registrado con éxito! Se envió un email de confirmación.",
            tipo: "success"
          });
          form.reset();
        } else {
          showAlert({
            mensaje: data.mensaje || "No se pudo registrar el turno.",
            tipo: "error"
          });
        }
      } catch (error) {
        showAlert({
          mensaje: "Error de conexión. Intenta nuevamente.",
          tipo: "error"
        });
      }
      if (enviarBtn) {
        enviarBtn.disabled = false;
      }
    });

    // Limpieza del formulario (opcional)
    form.addEventListener('reset', () => {
      // Si querés podés agregar una alerta al limpiar, pero no es obligatorio
      // showAlert({ mensaje: "Formulario limpio.", tipo: "info" });
    });
  }
});
