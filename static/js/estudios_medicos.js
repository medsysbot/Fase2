async function verEstudio() {
  const dni = document.getElementById('paciente_id').value.trim();
  const tipo = document.getElementById('tipo_estudio').value.trim();
  if (!dni || !tipo) {
    showAlert('error', 'Debe ingresar DNI y tipo de estudio.', false, 3000);
    return;
  }
  try {
    const resp = await fetch(`/ver_estudio/${dni}/${encodeURIComponent(tipo)}`);
    const data = await resp.json();
    if (data.exito) {
      document.getElementById('visorPDF').src = data.pdf_url;
      sessionStorage.setItem('pdfURL', data.pdf_url);
    } else {
      document.getElementById('visorPDF').src = '';
      showAlert('error', 'No se encontró el estudio solicitado', false, 3000);
    }
  } catch (e) {
    console.error(e);
    showAlert('error', 'No se pudo buscar el estudio', false, 3000);
  }
}

async function guardarEstudio() {
  const form = document.getElementById('form-estudio');
  const formData = new FormData(form);
  try {
    showAlert('guardado', 'Guardando estudio…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));
    const resp = await fetch('/guardar_estudio', {
      method: 'POST',
      body: formData
    });
    const data = await resp.json();
    if (data.exito) {
      showAlert('suceso', 'Estudio guardado', false, 3000);
      if (data.pdf_url) {
        document.getElementById('visorPDF').src = data.pdf_url;
        sessionStorage.setItem('pdfURL', data.pdf_url);
      }
    } else {
      showAlert('error', data.mensaje || 'Error al guardar', false, 4000);
    }
  } catch (e) {
    console.error(e);
    showAlert('error', 'Error al guardar', false, 4000);
  }
}

function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL');
  if (url) {
    window.open(url, '_blank');
  } else {
    showAlert('error', 'No hay PDF para mostrar', false, 3000);
  }
}
