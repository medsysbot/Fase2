// ╔════════════════════════════════════╗
// ║        registro_voz.js (AG-04)    ║
// ╚════════════════════════════════════╝
function marcarCamposVoz() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'es-AR';
  recognition.interimResults = false;
  recognition.continuous = false;

  recognition.onresult = (event) => {
    const texto = event.results[0][0].transcript.toLowerCase();
    console.log('Texto dictado:', texto);

    if (texto.includes('nombre')) {
      document.getElementById('nombres').value = limpiarCampo(texto, 'nombre');
    } else if (texto.includes('apellido')) {
      document.getElementById('apellido').value = limpiarCampo(texto, 'apellido');
    } else if (texto.includes('dni')) {
      document.getElementById('dni').value = limpiarCampo(texto, 'dni');
    } else if (texto.includes('fecha')) {
      const fechaTexto = limpiarCampo(texto, 'fecha').replace(/ de /g, '-');
      document.getElementById('fecha_nacimiento').value = convertirFecha(fechaTexto);
    } else if (texto.includes('tel')) {
      document.getElementById('telefono').value = limpiarCampo(texto, 'telefono');
    } else if (texto.includes('correo') || texto.includes('email')) {
      document.getElementById('email').value = limpiarCampo(texto, 'correo electronico');
    } else if (texto.includes('domicilio')) {
      document.getElementById('domicilio').value = limpiarCampo(texto, 'domicilio');
    } else if (texto.includes('obra social') || texto.includes('prepaga')) {
      document.getElementById('obra_social').value = limpiarCampo(texto, 'obra social');
    } else if (texto.includes('afiliado')) {
      document.getElementById('numero_afiliado').value = limpiarCampo(texto, 'numero de afiliado');
    } else if (texto.includes('emergencia')) {
      document.getElementById('contacto_emergencia').value = limpiarCampo(texto, 'contacto de emergencia');
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
