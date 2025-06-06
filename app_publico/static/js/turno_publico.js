// ╔═══════════════════════════════════╗
// ║   turno_publico.js (Público)      ║
// ╚═══════════════════════════════════╝

async function guardarPDF() {
  const form = document.getElementById('form-turnos');
  const formData = new FormData(form);

  const campos = ['nombre', 'apellido', 'dni', 'especialidad', 'profesional', 'fecha', 'hora', 'institucion'];
  for (const campo of campos) {
    const valor = form.querySelector(`[name="${campo}"]`).value.trim();
    if (!valor) {
      showAlert('error', 'Completa todos los campos.', false, 3000);
      return;
    }
  }

  try {
    showAlert('guardado', 'Guardando turno…', false, 3000);
    await new Promise(r => setTimeout(r, 1500));
    // Paso 1: guardar en la base de datos
    let resp = await fetch('/guardar_turno_publico', {
      method: 'POST',
      body: formData
    });
    let data = await resp.json();
    if (!resp.ok) {
      showAlert('error', data.mensaje || 'Error al guardar', false, 4000);
      return;
    }
    // Paso 2: generar el PDF
    resp = await fetch('/generar_pdf_turno_publico', {
      method: 'POST',
      body: formData
    });
    data = await resp.json();
    if (data.exito && data.pdf_url) {
      showAlert('suceso', 'Turno guardado', false, 3000);
      sessionStorage.setItem('pdfURL_turnos', data.pdf_url);
      sessionStorage.setItem('pdfURL', data.pdf_url);
      const btn = document.getElementById('btn-verpdf');
      if (btn) btn.style.display = 'inline-block';
    } else {
      showAlert('error', data.mensaje || 'Error al generar PDF', false, 4000);
    }
  } catch (error) {
    console.error('Error al guardar:', error);
    showAlert('error', 'Error al guardar', false, 4000);
  }
}

function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL_turnos');
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
    const res = await fetch('/obtener_email_paciente', { method: 'POST', body: formData });
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
  const url = sessionStorage.getItem('pdfURL_turnos');
  const email = await obtenerEmailPorDni(dni);

  if (!email) {
    showAlert('error', 'No se encontró un e-mail para este DNI.', false, 3000);
    return;
  }
  if (!url) {
    showAlert('error', 'Genera primero el PDF del turno.', false, 3000);
    return;
  }

  try {
    showAlert('email', 'Enviando e-mail…', false, 3000);
    await new Promise(r => setTimeout(r, 1500));

    const formData = new FormData();
    formData.append('nombre', nombre);
    formData.append('dni', dni);
    formData.append('pdf_url', url);

    const response = await fetch('/enviar_pdf_turno_publico', {
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

document.addEventListener('DOMContentLoaded', async () => {
  const instInput = document.getElementById('institucion_nombre');
  const btn = document.getElementById('btn-verpdf');
  if (instInput) instInput.value = sessionStorage.getItem('institucion_nombre') || '';
  if (btn) {
    const url = sessionStorage.getItem('pdfURL');
    btn.style.display = url ? 'inline-block' : 'none';
  }

  // AGREGADO: Llenar select de instituciones dinámicamente
  const selectInst = document.getElementById('institucion');
  if (selectInst) {
    try {
      const resp = await fetch('/api/listar_instituciones');
      const data = await resp.json();
      (data.instituciones || []).forEach(inst => {
        const opt = document.createElement('option');
        opt.value = inst.id;
        opt.textContent = inst.nombre;
        selectInst.appendChild(opt);
      });
    } catch (err) {
      showAlert && showAlert('error', 'No se pudieron cargar las instituciones.', false, 4000);
    }
  }
});
