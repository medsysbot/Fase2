// ╔════════════════════════════════════╗
// ║      guardar_receta.js      ║
// ╚════════════════════════════════════╝
async function guardarPDF() {
  const form = document.getElementById("form-receta");
  const formData = new FormData(form);
  formData.set('institucion_id', sessionStorage.getItem('institucion_id') || '');


  try {
    showAlert("guardado", "Guardando receta…", false, 3000);
    await new Promise(resolve => setTimeout(resolve, 3200));

    const response = await fetch('/guardar_receta_medica', {
      method: 'POST',
      body: formData
    });

    const resultado = await response.json();

    if (resultado.pdf_url) {
      showAlert("suceso", "Receta generada y guardada correctamente", false, 3000);
      sessionStorage.setItem('pdfURL_receta', resultado.pdf_url);
    } else {
      const mensaje = resultado.error || resultado.mensaje || "Error al guardar la receta";
      showAlert('error', mensaje, false, 4000);
    }
  } catch (error) {
    console.error('Error al guardar:', error);
    showAlert("error", "Error al guardar la receta", false, 4000);
  }
}

function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL_receta');
  if (url) {
    showAlert("cargaPDF", "Cargando PDF…", false, 3000);
    const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
    setTimeout(() => {
      if (isIOS) {
        window.location.href = url;
      } else {
        window.open(url, '_blank');
      }
    }, 1000);
  } else {
    showAlert("pdf", "Error Al Cargar El PDF", false, 3000);
  }
}


async function obtenerEmailPorDni(dni) {
  try {
    const formData = new FormData();
    formData.append('dni', dni);
    const res = await fetch('/obtener_email_receta', {
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
  const nombre = document.getElementById('nombre').value.trim();
  const dni = document.getElementById('dni').value.trim();
  const email = await obtenerEmailPorDni(dni);

  const pdfURL = sessionStorage.getItem('pdfURL_receta');
  if (!pdfURL) {
    showAlert('pdf', 'La receta no ha sido generada todavía', false, 3000);
    return;
  }

  if (!email) {
    showAlert('error', 'No se encontró un e-mail para este DNI.', false, 3000);
    return;
  }

  try {
    showAlert('email', 'Enviando e-mail…', false, 3000);
    await new Promise((r) => setTimeout(r, 3200));

    const formData = new FormData();
    formData.append('nombre', nombre);
    formData.append('dni', dni);
    formData.append('pdf_url', pdfURL);

    const response = await fetch('/enviar_pdf_receta', {
      method: 'POST',
      body: formData,
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
  const instInput = document.getElementById('institucion_id');
  if (instInput) {
    instInput.value = sessionStorage.getItem('institucion_id') || '';
  }
});

