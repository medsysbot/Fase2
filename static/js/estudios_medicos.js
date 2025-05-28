// ╔════════════════════════════════════╗
// ║      estudios_medicos.js      ║
// ╚════════════════════════════════════╝
// Funciones para visualizar y enviar estudios médicos
let estudioSeleccionado = null;

async function buscarEstudio() {
  const dni = document.getElementById('paciente_id').value.trim();
  const tipo = document.getElementById('tipo_estudio').value;
  const listaFechas = document.getElementById('lista-fechas');

  if (!dni || !tipo) {
    showAlert('error', 'Debe ingresar DNI y tipo de estudio.', false, 3000);
    return;
  }

  try {
    const resp = await fetch(`/consultar_estudios/${dni}`);
    const data = await resp.json();
  const lista = (data.estudios || []).filter(e => e.tipo_estudio === tipo);

  listaFechas.innerHTML = '';
  estudioSeleccionado = null;

    if (lista.length === 0) {
      document.getElementById('visorPDF').src = '';
      listaFechas.style.display = 'none';
      showAlert('error', 'No se encontraron estudios.', false, 3000);
      return;
    }

    if (lista.length === 1) {
      listaFechas.style.display = 'none';
      mostrarPDF(lista[0].id);
    } else {
    listaFechas.style.display = 'block';
    lista.forEach(e => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = '#';
      a.textContent = e.fecha_estudio;
      a.onclick = (ev) => { ev.preventDefault(); cargarEstudio(e.id); };
      li.appendChild(a);
      listaFechas.appendChild(li);
    });
    document.getElementById('visorPDF').src = '';
    showAlert('busqueda', 'Seleccione la fecha deseada', false, 3000);
  }
  } catch (err) {
    console.error(err);
    showAlert('error', 'Error al buscar estudios.', false, 3000);
  }
}

function cargarEstudio(id) {
  mostrarPDF(id);
}

async function mostrarPDF(id) {
  if (!id) return;
  try {
    const resp = await fetch(`/obtener_estudio/${id}`);
    const data = await resp.json();
    if (data.url_pdf) {
      document.getElementById('visorPDF').src = data.url_pdf;
      sessionStorage.setItem('pdfURL_estudios', data.url_pdf);
      document.getElementById('pdf_url').value = data.url_pdf;
      estudioSeleccionado = id;
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
  const idSeleccion = estudioSeleccionado;

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
      sessionStorage.setItem('pdfURL_estudios', data.pdf_url);
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
  const url = sessionStorage.getItem('pdfURL_estudios');
  if (url) {
    window.open(url, '_blank');
  } else {
    showAlert('error', 'No hay PDF para mostrar', false, 3000);
  }
}
