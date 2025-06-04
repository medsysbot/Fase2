// ╔════════════════════════════════════╗
// ║  historia_clinica_completa.js      ║
// ╚════════════════════════════════════╝

function closeAlert() {
  document.getElementById("alert-manager").style.display = "none";
}

document.getElementById("btn-no").onclick = closeAlert;
document.getElementById("btn-borrar").onclick = closeAlert;

/*──────────────────────────────────────────────*/
/*      GUARDAR Y GENERAR PDF                   */
/*──────────────────────────────────────────────*/
async function guardarFormulario() {
  const form = document.getElementById("form-historia");
  const datosFormulario = new FormData(form);
  try {
    showAlert("guardado", "Guardando Historia Clínica…", false, 3000);
    await new Promise((r) => setTimeout(r, 3200));

    let res = await fetch('/guardar_historia_clinica_completa', {
      method: 'POST',
      body: datosFormulario
    });
    const guardado = await res.json();

    if (!res.ok) {
      throw new Error(guardado.error || 'Error al guardar datos');
    }

    const datosPdf = new FormData();
    datosPdf.append('nombre', form.querySelector('#nombre').value.trim());
    datosPdf.append('apellido', form.querySelector('#apellido').value.trim());
    datosPdf.append('dni', form.querySelector('#dni').value.trim());

    res = await fetch('/generar_pdf_historia_clinica_completa', {
      method: 'POST',
      body: datosPdf
    });
    const resultado = await res.json();

    if (resultado.exito && resultado.pdf_url) {
      sessionStorage.setItem('pdfURL_historia', resultado.pdf_url);
      showAlert('suceso', 'Historia Clínica Guardada', false, 3000);
    } else {
      throw new Error(resultado.mensaje || 'Error al generar PDF');
    }
  } catch (e) {
    console.error('Error al guardar:', e);
    showAlert('error', e.message || 'Error Al Guardar', false, 4000);
  }
}

/*──────────────────────────────────────────────*/
/*        ENVIAR HISTORIA POR CORREO            */
/*──────────────────────────────────────────────*/
async function enviarPorCorreo() {
  const form = document.getElementById("form-historia");
  const nombre = `${form.querySelector('#nombre')?.value.trim() || ''} ${form.querySelector('#apellido')?.value.trim() || ''}`.trim();
  const dni = form.querySelector('#dni')?.value.trim() || '';
  const email = await obtenerEmailPorDni(dni);
  const pdfURL = sessionStorage.getItem('pdfURL_historia');

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
    formData.append('nombre', nombre);
    formData.append('dni', dni);
    formData.append('pdf_url', pdfURL);

    const res = await fetch('/enviar_pdf_historia_clinica_completa', {
      method: 'POST',
      body: formData
    });
    const json = await res.json();

    if (json.exito) {
      showAlert('suceso', 'E-mail enviado con éxito', false, 3000);
    } else {
      throw new Error(json.mensaje || 'Error al enviar el e-mail');
    }
  } catch (e) {
    console.error('Error al enviar:', e);
    showAlert('error', e.message || 'Error al enviar el e-mail', false, 3000);
  }
}

/*──────────────────────────────────────────────*/
/*              ABRIR PDF GUARDADO              */
/*──────────────────────────────────────────────*/
function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL_historia');
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

window.addEventListener('DOMContentLoaded', () => {
  const btnVer = document.querySelector("button[title='Ver PDF']");
  if (sessionStorage.getItem('pdfURL_historia')) {
    btnVer.style.display = 'inline-block';
  } else {
    btnVer.style.display = 'none';
  }
});
