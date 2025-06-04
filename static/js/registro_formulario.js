// ╔════════════════════════════════════╗
// ║   registro_formulario.js (AG-05)  ║
// ╚════════════════════════════════════╝
function mostrarBotonPDF(existe) {
  const btn = document.querySelector('.botones-flotantes button[onclick="abrirPDF()"]');
  if (btn) btn.style.display = existe ? 'inline-block' : 'none';
}

async function guardarPDF() {
  const form = document.getElementById('form-registro');
  const formData = new FormData(form);
  try {
    showAlert('guardado', 'Guardando datos…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));
    const resp = await fetch('/guardar_registro_paciente', {
      method: 'POST',
      body: formData
    });
    const data = await resp.json();
    if (data.message) {
      await generarPDF();
    } else {
      showAlert('error', data.error || 'Error al guardar', false, 4000);
    }
  } catch (e) {
    console.error('Error al guardar:', e);
    showAlert('error', 'Error al guardar', false, 4000);
  }
}

async function generarPDF() {
  const form = document.getElementById('form-registro');
  const fd = new FormData(form);
  try {
    const resp = await fetch('/generar_pdf_registro_paciente', {
      method: 'POST',
      body: fd
    });
    const data = await resp.json();
    if (data.pdf_url) {
      showAlert('suceso', 'Registro guardado', false, 3000);
      sessionStorage.setItem('pdfURL_registro_paciente', data.pdf_url);
      mostrarBotonPDF(true);
    } else {
      showAlert('error', data.error || 'Error al generar PDF', false, 4000);
    }
  } catch (e) {
    console.error('Error al generar PDF:', e);
    showAlert('error', 'Error al generar PDF', false, 4000);
  }
}

function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL_registro_paciente');
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
  const form = document.getElementById('form-registro');
  const fd = new FormData(form);
  const pdfURL = sessionStorage.getItem('pdfURL_registro_paciente');
  if (!pdfURL) {
    showAlert('pdf', 'Genera y guarda el registro antes de enviarlo.', false, 3000);
    return;
  }
  fd.append('pdf_url', pdfURL);
  try {
    showAlert('email', 'Enviando e-mail…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));
    const resp = await fetch('/enviar_pdf_registro_paciente', {
      method: 'POST',
      body: fd
    });
    const data = await resp.json();
    if (data.message) {
      showAlert('suceso', 'E-mail enviado con éxito', false, 3000);
    } else {
      showAlert('error', data.error || data.mensaje || 'Error al enviar el e-mail', false, 3000);
    }
  } catch (e) {
    console.error('Error al enviar:', e);
    showAlert('error', 'Error al enviar el e-mail', false, 3000);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  mostrarBotonPDF(!!sessionStorage.getItem('pdfURL_registro_paciente'));
});
