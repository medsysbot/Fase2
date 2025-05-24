function iniciarReconocimiento() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'es-AR';
  recognition.interimResults = false;
  recognition.continuous = false;

  recognition.onresult = (event) => {
    const texto = event.results[0][0].transcript.toLowerCase();
    console.log('Texto dictado:', texto);

    if (texto.includes('nombre')) {
      document.getElementById('nombre').value = limpiarCampo(texto, 'nombre');
    } else if (texto.includes('dni')) {
      document.getElementById('dni').value = limpiarCampo(texto, 'dni');
    } else if (texto.includes('fecha')) {
      const fechaTexto = limpiarCampo(texto, 'fecha').replace(/ de /g, '-');
      document.getElementById('fecha').value = convertirFecha(fechaTexto);
    } else if (texto.includes('diagnostico') || texto.includes('diagnóstico')) {
      document.getElementById('diagnostico').value = limpiarCampo(texto, 'diagnostico');
    } else if (texto.includes('medicamentos')) {
      document.getElementById('medicamentos').value = limpiarCampo(texto, 'medicamentos');
    }
  };

  recognition.onerror = (e) => console.error('Error de voz:', e.error);
  recognition.start();
}

function limpiarCampo(texto, campo) {
  return texto.replace(campo, '').replace('dos puntos', ':').trim();
}

function convertirFecha(texto) {
  try {
    if (texto.includes('-')) {
      let partes = texto.split('-');
      return `${partes[2]}-${partes[1].padStart(2, '0')}-${partes[0].padStart(2, '0')}`;
    } else {
      return texto;
    }
  } catch (e) {
    return '';
  }
}

document.addEventListener('keydown', (e) => {
  if (e.code === 'Space') {
    e.preventDefault();
    iniciarReconocimiento();
  }
});
