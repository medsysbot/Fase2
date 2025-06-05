// ╔═══════════════════════════════════╗
// ║  turnos_pacientes.js              ║
// ╚═══════════════════════════════════╝
async function guardarPDF() {
  const form = document.getElementById('form-turnos');
  const formData = new FormData(form);
  const campos = ['nombre', 'apellido', 'dni', 'especialidad', 'profesional', 'fecha', 'hora'];
  for (const campo of campos) {
    const valor = form.querySelector(`[name="${campo}"]`).value.trim();
    if (!valor) {
      showAlert('error', 'Completa todos los campos.', false, 3000);
      return;
    }
  }
  try {
    showAlert('guardado', 'Guardando turno…', false, 3000);
    await new Promise(r => setTimeout(r, 1500));
    let resp = await fetch('/guardar_turno_paciente', { method: 'POST', body: formData });
    let data = await resp.json();
    if (!resp.ok) {
      showAlert('error', data.mensaje || 'Error al guardar', false, 4000);
      return;
    }
    resp = await fetch('/generar_pdf_turno_paciente', { method: 'POST', body: formData });
    data = await resp.json();
    if (data.exito && data.pdf_url) {
      showAlert('suceso', 'Turno guardado', false, 3000);
      sessionStorage.setItem('pdfURL_turnos', data.pdf_url);
      sessionStorage.setItem('pdfURL', data.pdf_url);
      const btn = document.getElementById('btn-verpdf');
      if (btn) btn.style.display = 'inline-block';
    } else {
      showAlert('error', data.mensaje || 'Error al generar PDF', false, 4000);
    }
  } catch (error) {
    console.error('Error al guardar:', error);
    showAlert('error', 'Error al guardar', false, 4000);
  }
}

function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL_turnos');
  if (url) {
    showAlert('cargaPDF', 'Cargando PDF…', false, 3000);
    const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
    setTimeout(() => {
      if (isIOS) {
        window.location.href = url;
      } else {
        window.open(url, '_blank');
      }
    }, 1000);
  } else {
    showAlert('pdf', 'Error al cargar el PDF', false, 3000);
  }
}

async function obtenerEmailPorDni(dni) {
  try {
    const fd = new FormData();
    fd.append('dni', dni);
    const res = await fetch('/obtener_email_paciente', { method: 'POST', body: fd });
    const data = await res.json();
    return data.email || null;
  } catch (e) {
    console.error('Error al obtener email:', e);
    return null;
  }
}

async function enviarPorCorreo() {
  const nombre = document.querySelector('[name="nombre"]').value.trim();
  const apellido = document.querySelector('[name="apellido"]').value.trim();
  const dni = document.querySelector('[name="dni"]').value.trim();
  const url = sessionStorage.getItem('pdfURL_turnos');
  const email = await obtenerEmailPorDni(dni);

  if (!email) {
    showAlert('error', 'No se encontró un e-mail para este DNI.', false, 3000);
    return;
  }
  if (!url) {
    showAlert('error', 'Genera primero el PDF del turno.', false, 3000);
    return;
  }

  try {
    showAlert('email', 'Enviando e-mail…', false, 3000);
    await new Promise(r => setTimeout(r, 1500));
    const fd = new FormData();
    fd.append('nombre', `${nombre} ${apellido}`.trim());
    fd.append('dni', dni);
    fd.append('pdf_url', url);
    const response = await fetch('/enviar_pdf_turno_paciente', { method: 'POST', body: fd });
    const resultado = await response.json();
    if (resultado.exito) {
      showAlert('suceso', 'E-mail enviado con éxito', false, 3000);
    } else {
      showAlert('error', resultado.mensaje || 'Error al enviar el e-mail', false, 3000);
    }
  } catch (error) {
    console.error('Error al enviar:', error);
    showAlert('error', 'Error al enviar el e-mail', false, 3000);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('btn-verpdf');
  if (btn) {
    const url = sessionStorage.getItem('pdfURL_turnos');
    btn.style.display = url ? 'inline-block' : 'none';
  }
});

function iniciarReconocimientoVozTurnos() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'es-AR';
  recognition.interimResults = false;
  recognition.continuous = false;

  recognition.onresult = (event) => {
    const texto = event.results[0][0].transcript.toLowerCase();
    const campos = {
      'nombre': 'nombre',
      'apellido': 'apellido',
      'dni': 'dni',
      'especialidad': 'especialidad',
      'profesional': 'profesional',
      'fecha': 'fecha',
      'horario': 'hora',
      'hora': 'hora',
      'observaciones': 'observaciones'
    };

    for (const clave in campos) {
      if (texto.includes(clave)) {
        const idCampo = campos[clave];
        let valor = texto.replace(clave, '').replace('dos puntos', ':').trim();
        if (idCampo === 'fecha') {
          valor = convertirFecha(valor.replace(/ de /g, '-'));
        }
        const campo = document.getElementById(idCampo);
        if (campo) campo.value = valor;
        break;
      }
    }
  };

  recognition.onerror = (e) => console.error('Error de voz:', e.error);
  recognition.start();
}

function convertirFecha(texto) {
  try {
    if (texto.includes('-')) {
      const partes = texto.split('-');
      return `${partes[2]}-${partes[1].padStart(2, '0')}-${partes[0].padStart(2, '0')}`;
    }
    return texto;
  } catch (e) {
    return '';
  }
}
