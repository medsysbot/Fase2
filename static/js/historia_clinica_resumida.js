// ╔═══════════════════════════════════════════════════════════╗
// ║  historia_clinica_resumida.js - Manejo de formulario      ║
// ╚═══════════════════════════════════════════════════════════╝

function closeAlert() {
  document.getElementById("alert-manager").style.display = "none";
}

function mostrarBotonPDF(existe) {
  const btn = document.getElementById('btn-ver-pdf');
  if (btn) btn.style.display = existe ? 'block' : 'none';
}

async function guardarPDF() {
  const form = document.getElementById('form-resumen');
  const formData = new FormData(form);
  const nombre = form.querySelector('#nombre').value.trim();
  const apellido = form.querySelector('#apellido').value.trim();
  formData.append('nombre', nombre);
  formData.append('apellido', apellido);

  try {
    showAlert('guardado', 'Guardando Historia Clínica…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));
    const response = await fetch('/generar_pdf_historia_clinica_resumida', {
      method: 'POST',
      body: formData
    });
    const resultado = await response.json();
    if (resultado.exito && resultado.pdf_url) {
      showAlert('suceso', 'Historia Clínica Guardada', false, 3000);
      sessionStorage.setItem('pdfURL_historia_resumida', resultado.pdf_url);
      mostrarBotonPDF(true);
    } else {
      showAlert('error', resultado.mensaje || 'Error al guardar', false, 4000);
    }
  } catch (error) {
    console.error('Error al guardar:', error);
    showAlert('error', 'Error al guardar', false, 4000);
  }
}

async function enviarPorCorreo() {
  const form = document.getElementById('form-resumen');
  const nombre = form.querySelector('#nombre')?.value.trim() || '';
  const apellido = form.querySelector('#apellido')?.value.trim() || '';
  const paciente = `${nombre} ${apellido}`.trim();
  const dni = form.querySelector('[name="dni"]')?.value.trim() || '';
  const pdfURL = sessionStorage.getItem('pdfURL_historia_resumida');
  const email = await obtenerEmailPorDni(dni);

  if (!pdfURL) {
    showAlert('pdf', 'Genera y guarda la historia clínica antes de enviarla.', false, 3000);
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
    formData.append('nombre', paciente);
    formData.append('dni', dni);
    formData.append('pdf_url', pdfURL);
    const response = await fetch('/enviar_pdf_historia_clinica_resumida', {
      method: 'POST',
      body: formData
    });
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

function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL_historia_resumida');
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

// Mostrar botón PDF si hay URL almacenada
mostrarBotonPDF(!!sessionStorage.getItem('pdfURL_historia_resumida'));
