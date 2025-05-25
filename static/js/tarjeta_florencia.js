document.addEventListener('DOMContentLoaded', () => {
  const btnMusica = document.getElementById('btn-musica');
  const audio = document.getElementById('audio-fondo');
  const contador = document.getElementById('contador');

  if (btnMusica && audio) {
    btnMusica.addEventListener('click', () => {
      if (audio.paused) {
        audio.play();
        btnMusica.textContent = '⏸️';
      } else {
        audio.pause();
        btnMusica.textContent = '▶️';
      }
    });
  }

  if (contador) {
    const fechaObjetivo = new Date();
    fechaObjetivo.setMonth(fechaObjetivo.getMonth() + 4);
    fechaObjetivo.setSeconds(0, 0);

    function actualizarContador() {
      const ahora = new Date();
      const diff = fechaObjetivo - ahora;
      if (diff <= 0) {
        contador.textContent = '¡Llegó el gran día!';
        return;
      }
      const dias = Math.floor(diff / (1000 * 60 * 60 * 24));
      const horas = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutos = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      contador.textContent = `${dias}d ${horas}h ${minutos}m`;
    }

    actualizarContador();
    setInterval(actualizarContador, 60000);
  }

  const imagenes = document.querySelectorAll('.galeria img');
  let indice = 0;
  if (imagenes.length > 0) {
    setInterval(() => {
      imagenes[indice].classList.remove('active');
      indice = (indice + 1) % imagenes.length;
      imagenes[indice].classList.add('active');
    }, 3000);
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
      console.log('Confirmación:', data);
      alert('¡Gracias por confirmar!');
      formConfirmacion.reset();
    });
  }
});
