document.addEventListener('DOMContentLoaded', () => {
  const contador = document.getElementById('contador');
  if (contador) {
    const fechaObjetivo = new Date();
    fechaObjetivo.setMonth(fechaObjetivo.getMonth() + 4);
    fechaObjetivo.setHours(0,0,0,0);

    function actualizarContador() {
      const ahora = new Date();
      const diff = fechaObjetivo - ahora;
      const dias = Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
      contador.textContent = `${dias} días para su cumpleaños`;
    }

    actualizarContador();
    setInterval(actualizarContador, 86400000);

    setTimeout(() => {
      window.location.href = '/confirmacion-florencia';
    }, 8000);
  }

  const formConfirmacion = document.getElementById('form-confirmacion');
  if (formConfirmacion) {
    formConfirmacion.addEventListener('submit', (e) => {
      e.preventDefault();
      const data = {
        nombre: formConfirmacion.nombre.value,
        asistira: formConfirmacion.asistira.value,
        comentarios: formConfirmacion.comentarios.value
      };
      localStorage.setItem('confirmacionFlorencia', JSON.stringify(data));
      console.log('Datos guardados:', data);
      alert('¡Gracias por confirmar!');
    });
  }
});
