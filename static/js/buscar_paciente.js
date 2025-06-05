// ╔════════════════════════════════════╗
// ║   buscar_paciente.js (AG-07)      ║
// ╚════════════════════════════════════╝

let pdfURL = null;

function mostrarCampoEmail() {
  document.getElementById('email-envio-container').style.display = 'block';
}

async function enviarPorCorreo() {
  const email = document.getElementById('email-destino').value.trim();
  const dni = document.getElementById('dni-paciente').value.trim();

  if (!email) {
    showAlert('alerta', 'Ingrese un email', false, 3000);
    return;
  }
  if (!pdfURL) {
    showAlert('pdf', 'Genere y guarde antes de enviar.', false, 3000);
    return;
  }

  try {
    showAlert('email', 'Enviando e-mail…', false, 3000);
    await new Promise(r => setTimeout(r, 1500));
    const fd = new FormData();
    fd.append('dni', dni);
    fd.append('email', email);
    fd.append('pdf_url', pdfURL);
    const resp = await fetch('/enviar_pdf_busqueda', { method: 'POST', body: fd });
    const data = await resp.json();
    if (data.exito) {
      showAlert('suceso', 'E-mail enviado con éxito', false, 3000);
      document.getElementById('email-envio-container').style.display = 'none';
    } else {
      showAlert('error', data.mensaje || 'Error al enviar el e-mail', false, 3000);
    }
  } catch (error) {
    console.error('Error al enviar:', error);
    showAlert('error', 'Error al enviar el e-mail', false, 3000);
  }
}

function iconoEstado(ok) {
  if (ok === null) return '⏳';
  return ok ? '✅' : '❌';
}

function iniciarReconocimientoVoz() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'es-AR';
  recognition.interimResults = false;
  recognition.continuous = false;
  recognition.onresult = (event) => {
    const texto = event.results[0][0].transcript.replace(/\D/g, '');
    document.getElementById('dni-paciente').value = texto;
  };
  recognition.onerror = () => showAlert('error', 'No se pudo reconocer la voz', false, 3000);
  recognition.start();
}

async function buscarPaciente(dni) {
  showAlert('busqueda', 'Buscando…', false, 2000);
  const resp = await fetch('/api/buscar_paciente', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dni })
  });
  const data = await resp.json();
  pdfURL = data.pdf_url || null;
  document.getElementById('btn-verpdf').style.display = pdfURL ? 'inline-block' : 'none';
  document.getElementById('hc-completa-icon').textContent = iconoEstado(data.historia_clinica_completa);
  document.getElementById('hc-resumida-icon').textContent = iconoEstado(data.historia_clinica_resumida);
  document.getElementById('hc-diaria-icon').textContent = iconoEstado(data.consulta_diaria);
  document.getElementById('recetas-icon').textContent = iconoEstado(data.recetas);
  document.getElementById('turnos-icon').textContent = iconoEstado(data.turnos);
  document.getElementById('estudios-icon').textContent = iconoEstado(data.estudios);
  document.getElementById('resultados-busqueda').style.display = 'block';
}

async function guardarPaciente() {
  const dni = document.getElementById('dni-paciente').value;
  if (!dni) { showAlert('alerta', 'Ingrese un DNI válido', false, 3000); return; }
  showAlert('guardado', 'Generando PDF…', false, 3000);
  const resp = await fetch('/api/guardar_paciente', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dni })
  });
  const data = await resp.json();
  if (data.ok) {
    pdfURL = data.pdf_url || null;
    document.getElementById('btn-verpdf').style.display = pdfURL ? 'inline-block' : 'none';
    showAlert('suceso', 'Paciente guardado', false, 3000);
  } else {
    showAlert('error', data.error || 'No se pudo guardar', false, 4000);
  }
}

function verPDF() {
  if (pdfURL) {
    window.open(pdfURL, '_blank');
  } else {
    showAlert('pdf', 'No hay PDF para mostrar', false, 3000);
  }
}

function prepararBorradoPaciente() {
  document.getElementById('confirmacion-borrado').style.display = 'block';
}

function cancelarBorradoPaciente() {
  document.getElementById('confirmacion-borrado').style.display = 'none';
}

async function confirmarBorradoPaciente() {
  const dni = document.getElementById('dni-paciente').value;
  cancelarBorradoPaciente();
  if (!dni) { showAlert('alerta', 'Ingrese un DNI', false, 3000); return; }
  showAlert('borrado', 'Borrando paciente…', false, 3000);
  const resp = await fetch('/api/borrar_paciente', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dni })
  });
  const data = await resp.json();
  if (data.ok) {
    showAlert('suceso', 'Paciente borrado', false, 3000);
    document.getElementById('resultados-busqueda').style.display = 'none';
    document.getElementById('btn-verpdf').style.display = 'none';
  } else {
    showAlert('error', data.error || 'No se pudo borrar', false, 4000);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('form-busqueda-paciente');
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const dni = document.getElementById('dni-paciente').value;
    if (!dni) { showAlert('alerta', 'Ingrese un DNI válido', false, 3000); return; }
    buscarPaciente(dni);
  });
  document.getElementById('btn-no').onclick = cancelarBorradoPaciente;
  document.getElementById('btn-borrar').onclick = confirmarBorradoPaciente;
});
