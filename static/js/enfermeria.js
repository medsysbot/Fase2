// ╔═══════════════════════════════════╗
// ║   enfermeria.js                   ║
// ╚═══════════════════════════════════╝
async function guardarEnfermeria() {
  const form = document.getElementById('form-enfermeria');
  const formData = new FormData(form);
  formData.set('institucion_id', sessionStorage.getItem('institucion_id') || '');
  formData.set('usuario_id', sessionStorage.getItem('usuario_id') || '');

  const campos = [
    'nombre', 'apellido', 'dni', 'edad', 'altura', 'peso', 'hora',
    'temperatura', 'glucemia', 'glasgow', 'saturacion', 'frecuencia_cardiaca',
    'ta', 'tad', 'dolor', 'triaje', 'motivo_consulta', 'profesional',
    'presion_arterial', 'observaciones'
  ];
  for (const c of campos) {
    const valor = form.querySelector(`[name="${c}"]`).value.trim();
    if (!valor) {
      showAlert('error', 'Completa todos los campos.', false, 3000);
      return;
    }
  }

  try {
    showAlert('guardado', 'Guardando datos…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));

    const resp = await fetch('/generar_pdf_enfermeria', { method: 'POST', body: formData });
    const resultado = await resp.json();

    if (resultado.exito && resultado.pdf_url) {
      showAlert('suceso', 'Datos guardados', false, 3000);
      sessionStorage.setItem('pdfURL_enfermeria', resultado.pdf_url);
      sessionStorage.setItem('pdfURL', resultado.pdf_url);
      const btn = document.getElementById('btn-verpdf');
      if (btn) btn.style.display = 'inline-block';
    } else {
      showAlert('error', resultado.mensaje || 'Error al guardar', false, 4000);
    }
  } catch (e) {
    console.error('Error al guardar:', e);
    showAlert('error', 'Error al guardar', false, 4000);
  }
}

function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL_enfermeria');
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

async function enviarPorCorreo() {
  const nombre = document.querySelector('[name="nombre"]').value.trim();
  const apellido = document.querySelector('[name="apellido"]').value.trim();
  const paciente = `${nombre} ${apellido}`.trim();
  const dni = document.querySelector('[name="dni"]').value.trim();
  const pdfURL = sessionStorage.getItem('pdfURL_enfermeria');

  if (!pdfURL) {
    showAlert('pdf', 'Genera y guarda antes de enviar.', false, 3000);
    return;
  }

  try {
    showAlert('email', 'Enviando e-mail…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));

    const fd = new FormData();
    fd.append('paciente', paciente);
    fd.append('dni', dni);

    const res = await fetch('/enviar_pdf_enfermeria', { method: 'POST', body: fd });
    const resultado = await res.json();

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
    const url = sessionStorage.getItem('pdfURL');
    btn.style.display = url ? 'inline-block' : 'none';
  }
});

