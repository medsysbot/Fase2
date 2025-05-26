// ╔════════════════════════════════════╗
// ║      estudios_medicos.js      ║
// ╚════════════════════════════════════╝
// Funciones para visualizar y enviar estudios médicos
async function buscarEstudio() {
  const dni = document.getElementById('paciente_id').value.trim();
  const tipo = document.getElementById('tipo_estudio').value;
  const fechaSelect = document.getElementById('fecha');
  const labelFecha = document.getElementById('label-fecha');

  if (!dni || !tipo) {
    showAlert('error', 'Debe ingresar DNI y tipo de estudio.', false, 3000);
    return;
  }

  try {
    const resp = await fetch(`/consultar_estudios/${dni}`);
    const data = await resp.json();
    const lista = (data.estudios || []).filter(e => e.tipo_estudio === tipo);

    fechaSelect.innerHTML = '';
    fechaSelect.dataset.id = '';

    if (lista.length === 0) {
      labelFecha.style.display = 'none';
      fechaSelect.style.display = 'none';
      document.getElementById('visorPDF').src = '';
      showAlert('error', 'No se encontraron estudios.', false, 3000);
      return;
    }

    if (lista.length === 1) {
      labelFecha.style.display = 'none';
      fechaSelect.style.display = 'none';
      fechaSelect.dataset.id = lista[0].id;
      mostrarPDF(lista[0].id);
    } else {
      labelFecha.style.display = 'block';
      fechaSelect.style.display = 'block';
      const optBase = document.createElement('option');
      optBase.value = '';
      optBase.textContent = 'Seleccione fecha...';
      fechaSelect.appendChild(optBase);
      lista.forEach(e => {
        const opt = document.createElement('option');
        opt.value = e.id;
        opt.textContent = e.fecha_estudio;
        fechaSelect.appendChild(opt);
      });
      document.getElementById('visorPDF').src = '';
      showAlert('busqueda', 'Seleccione la fecha deseada', false, 3000);
    }
  } catch (err) {
    console.error(err);
    showAlert('error', 'Error al buscar estudios.', false, 3000);
  }
}

async function mostrarPDF(id) {
  if (!id) return;
  try {
    const resp = await fetch(`/obtener_estudio/${id}`);
    const data = await resp.json();
    if (data.url_pdf) {
      document.getElementById('visorPDF').src = data.url_pdf;
      sessionStorage.setItem('pdfURL', data.url_pdf);
      document.getElementById('pdf_url').value = data.url_pdf;
    } else {
      showAlert('error', 'No se encontró el PDF.', false, 3000);
    }
  } catch (err) {
    console.error(err);
    showAlert('error', 'Error al cargar el PDF.', false, 3000);
  }
}

async function enviarPorCorreo() {
  const dni = document.getElementById('paciente_id').value.trim();
  const idSeleccion = document.getElementById('fecha').value || document.getElementById('fecha').dataset.id;

  if (!dni || !idSeleccion) {
    showAlert('error', 'Debe seleccionar un estudio.', false, 3000);
    return;
  }

  try {
    showAlert('email', 'Enviando e-mail…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));
    const formData = new FormData();
    formData.append('dni', dni);
    formData.append('estudio_id', idSeleccion);
    const resp = await fetch('/enviar_pdf_estudio', { method: 'POST', body: formData });
    const data = await resp.json();
    if (data.exito) {
      showAlert('suceso', 'E-mail enviado', false, 3000);
    } else {
      showAlert('error', data.mensaje || 'Error al enviar', false, 3000);
    }
  } catch (err) {
    console.error(err);
    showAlert('error', 'Error al enviar el e-mail', false, 3000);
  }
}

async function guardarEstudio() {
  const form = document.getElementById('form-estudio');
  const formData = new FormData(form);
  try {
    showAlert('guardado', 'Guardando estudio…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));
    const resp = await fetch('/guardar_estudio', { method: 'POST', body: formData });
    const data = await resp.json();
    if (data.exito && data.pdf_url) {
      showAlert('suceso', 'Estudio guardado', false, 3000);
      document.getElementById('visorPDF').src = data.pdf_url;
      sessionStorage.setItem('pdfURL', data.pdf_url);
      document.getElementById('pdf_url').value = data.pdf_url;
    } else {
      showAlert('error', data.mensaje || 'Error al guardar', false, 4000);
    }
  } catch (err) {
    console.error(err);
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

// Cuando el usuario selecciona una fecha se carga el PDF correspondiente
document.getElementById('fecha').addEventListener('change', function (e) {
  mostrarPDF(e.target.value);
});
