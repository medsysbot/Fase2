document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('form-turnos');
  const alerta = document.getElementById('alerta-turno');
  const enviarBtn = document.getElementById('enviar-btn');

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      alerta.style.display = "none";
      enviarBtn.disabled = true;
      enviarBtn.textContent = "Enviando...";

      // Tomar datos del formulario
      const formData = new FormData(form);

      try {
        const response = await fetch('/solicitar_turno_publico', {
          method: 'POST',
          body: formData
        });

        const data = await response.json();

        if (data.exito) {
          alerta.textContent = "¡Turno registrado con éxito! Se envió un email de confirmación.";
          alerta.style.color = "#27ae60";
          alerta.style.display = "block";
          form.reset();
        } else {
          alerta.textContent = data.mensaje || "No se pudo registrar el turno.";
          alerta.style.color = "#e74c3c";
          alerta.style.display = "block";
        }
      } catch (error) {
        alerta.textContent = "Error de conexión. Intenta nuevamente.";
        alerta.style.color = "#e74c3c";
        alerta.style.display = "block";
      }
      enviarBtn.disabled = false;
      enviarBtn.textContent = "Enviar";
    });
  }
});
