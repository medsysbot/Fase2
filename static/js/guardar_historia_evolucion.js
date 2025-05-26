// ╔════════════════════════════════════╗
// ║      guardar_historia_evolucion.js ║
// ╚════════════════════════════════════╝

async function guardarPDF() {
  const form = document.getElementById('form-evolucion');
  const formData = new FormData(form);

  const firma = document.getElementById('firma');
  const sello = document.getElementById('sello');
  if (firma && firma.files.length > 0) {
    formData.append('firma', firma.files[0]);
  }
  if (sello && sello.files.length > 0) {
    formData.append('sello', sello.files[0]);
  }

  try {
    showAlert('guardado', 'Guardando evolución…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));

    const response = await fetch('/generar_pdf_evolucion', {
      method: 'POST',
      body: formData
    });
    const resultado = await response.json();

    if (resultado.exito && resultado.pdf_url) {
      showAlert('suceso', 'Evolución guardada', false, 3000);
      sessionStorage.setItem('pdfURL_evolucion', resultado.pdf_url);
    } else {
      showAlert('error', resultado.mensaje || 'Error al guardar', false, 4000);
    }
  } catch (error) {
    console.error('Error al guardar:', error);
    showAlert('error', 'Error al guardar', false, 4000);
  }
}

function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL_evolucion');
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
    const res = await fetch('/obtener_email_evolucion', {
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
  await guardarPDF();
  const paciente = document.getElementById('paciente').value.trim();
  const dni = document.getElementById('dni').value.trim();
  const email = await obtenerEmailPorDni(dni);

  if (!email) {
    showAlert('error', 'No se encontró un e-mail para este DNI.', false, 3000);
    return;
  }

  try {
    showAlert('email', 'Enviando e-mail…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));

    const formData = new FormData();
    formData.append('paciente', paciente);
    formData.append('dni', dni);

    const response = await fetch('/enviar_pdf_evolucion', {
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
