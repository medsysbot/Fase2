// ╔════════════════════════════════════╗
// ║   registro_pacientes.js (AG-05)   ║
// ╚════════════════════════════════════╝
function mostrarBotonPDF(existe) {
  const btn = document.getElementById('btn-ver-pdf');
  if (btn) btn.style.display = existe ? 'inline-block' : 'none';
}

async function guardarDatos() {
  const form = document.getElementById('form-registro-paciente');
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
  const nombres = document.getElementById('nombres').value.trim();
  const apellido = document.getElementById('apellido').value.trim();
  const dni = document.getElementById('dni').value.trim();
  const fd = new FormData();
  fd.append('nombres', nombres);
  fd.append('apellido', apellido);
  fd.append('dni', dni);
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

async function enviarPDF() {
  const nombres = document.getElementById('nombres').value.trim();
  const apellido = document.getElementById('apellido').value.trim();
  const dni = document.getElementById('dni').value.trim();
  const pdfURL = sessionStorage.getItem('pdfURL_registro_paciente');
  if (!pdfURL) {
    showAlert('pdf', 'Genera y guarda el registro antes de enviarlo.', false, 3000);
    return;
  }
  try {
    showAlert('email', 'Enviando e-mail…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));
    const fd = new FormData();
    fd.append('nombres', nombres);
    fd.append('apellido', apellido);
    fd.append('dni', dni);
    fd.append('pdf_url', pdfURL);
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
