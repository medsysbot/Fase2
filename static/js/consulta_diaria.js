// ╔═══════════════════════════════════╗
// ║   consulta_diaria.js              ║
// ╚═══════════════════════════════════╝
async function guardarPDF() {
  const form = document.getElementById('form-consulta');
  const formData = new FormData(form);
  formData.set('institucion_id', sessionStorage.getItem('institucion_id') || '');
  formData.set('usuario_id', sessionStorage.getItem('usuario_id') || '');

  try {
    showAlert('guardado', 'Guardando consulta…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));

    const response = await fetch('/generar_pdf_consulta_diaria', {
      method: 'POST',
      body: formData
    });
    const resultado = await response.json();

    if (resultado.pdf_url) {
      showAlert('suceso', 'Consulta guardada', false, 3000);
      sessionStorage.setItem('pdfURL_consulta_diaria', resultado.pdf_url);
      const btn = document.getElementById('btn-verpdf');
      if (btn) btn.style.display = 'inline-block';
    } else {
      showAlert('error', resultado.error || 'Error al guardar', false, 4000);
    }
  } catch (e) {
    console.error('Error al guardar:', e);
    showAlert('error', 'Error al guardar', false, 4000);
  }
}

function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL_consulta_diaria');
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
    showAlert('pdf', 'Error Al Cargar El PDF', false, 3000);
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

async function enviarPDF() {
  const nombre = document.getElementById('nombre').value.trim();
  const apellido = document.getElementById('apellido').value.trim();
  const dni = document.getElementById('dni').value.trim();
  const pdfURL = sessionStorage.getItem('pdfURL_consulta_diaria');
  const email = await obtenerEmailPorDni(dni);

  if (!pdfURL) {
    showAlert('pdf', 'Genera y guarda la consulta antes de enviarla.', false, 3000);
    return;
  }

  if (!email) {
    showAlert('error', 'No se encontró un e-mail para este DNI.', false, 3000);
    return;
  }

  try {
    showAlert('email', 'Enviando e-mail…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));

    const formData = new FormData();
    formData.append('dni', dni);
    formData.append('pdf_url', pdfURL);
    formData.append('nombre', `${nombre} ${apellido}`.trim());

    const response = await fetch('/enviar_pdf_consulta_diaria', {
      method: 'POST',
      body: formData
    });
    const resultado = await response.json();

    if (resultado.message) {
      showAlert('suceso', 'E-mail enviado con éxito', false, 3000);
    } else {
      showAlert('error', resultado.error || 'Error al enviar el e-mail', false, 3000);
    }
  } catch (error) {
    console.error('Error al enviar:', error);
    showAlert('error', 'Error al enviar el e-mail', false, 3000);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('btn-verpdf');
  if (btn) {
    const url = sessionStorage.getItem('pdfURL_consulta_diaria');
    btn.style.display = url ? 'inline-block' : 'none';
  }
});
