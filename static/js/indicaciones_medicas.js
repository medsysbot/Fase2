// ╔════════════════════════════════════╗
// ║      guardar_indicaciones.js      ║
// ╚════════════════════════════════════╝
async function guardarPDF() {
  const form = document.getElementById('form-indicaciones');
  const formData = new FormData(form);


  try {
    showAlert('guardado', 'Guardando indicaciones…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));

    const response = await fetch('/generar_pdf_indicacion_medica', {
      method: 'POST',
      body: formData
    });
    const resultado = await response.json();

    if (resultado.exito && resultado.pdf_url) {
      showAlert('suceso', 'Indicaciones guardadas', false, 3000);
      sessionStorage.setItem('pdfURL_indicaciones_medicas', resultado.pdf_url);
      const btn = document.getElementById('btn-verpdf');
      if (btn) btn.style.display = 'inline-block';
    } else {
      showAlert('error', resultado.mensaje || 'Error al guardar', false, 4000);
    }
  } catch (error) {
    console.error('Error al guardar:', error);
    showAlert('error', 'Error al guardar', false, 4000);
  }
}

function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL_indicaciones_medicas');
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
    const formData = new FormData();
    formData.append('dni', dni);
    const res = await fetch('/obtener_email_paciente', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    return data.email || null;
  } catch (e) {
    console.error('Error al obtener email:', e);
    return null;
  }
}

async function enviarPorCorreo() {
  const nombre = document.querySelector('[name="nombre"]').value.trim();
  const dni = document.querySelector('[name="dni"]').value.trim();
  const email = await obtenerEmailPorDni(dni);
  const pdfURL = sessionStorage.getItem('pdfURL_indicaciones_medicas');

  if (!pdfURL) {
    showAlert('pdf', 'Genera y guarda las indicaciones antes de enviarlas.', false, 3000);
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
    formData.append('nombre', nombre);
    formData.append('dni', dni);
    formData.append('pdf_url', pdfURL);

    const response = await fetch('/enviar_pdf_indicacion_medica', {
      method: 'POST',
      body: formData
    });
    const resultado = await response.json();

    if (resultado.exito) {
      showAlert('suceso', 'E-mail enviado con éxito', false, 3000);
    } else {
      showAlert('error', 'Error al enviar el e-mail', false, 3000);
    }
  } catch (error) {
    console.error('Error al enviar:', error);
    showAlert('error', 'Error al enviar el e-mail', false, 3000);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('btn-verpdf');
  if (btn) {
    const url = sessionStorage.getItem('pdfURL_indicaciones_medicas');
    btn.style.display = url ? 'inline-block' : 'none';
  }
});
