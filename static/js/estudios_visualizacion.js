async function buscarEstudios() {
  const dni = document.getElementById('dni').value.trim();
  if (!dni) return;
  try {
    const resp = await fetch(`/consultar_estudios/${dni}`);
    const data = await resp.json();
    const select = document.getElementById('lista-estudios');
    select.innerHTML = '<option value="">Seleccione un estudio...</option>';
    if (data.estudios) {
      data.estudios.forEach(e => {
        const opt = document.createElement('option');
        opt.value = e.id;
        opt.textContent = `${e.tipo_estudio} (${e.fecha_estudio})`;
        select.appendChild(opt);
      });
    }
    document.getElementById('visor').src = '';
  } catch (err) {
    console.error('Error al buscar estudios', err);
  }
}

async function mostrarEstudio(id) {
  if (!id) { document.getElementById('visor').src = ''; return; }
  try {
    const resp = await fetch(`/obtener_estudio/${id}`);
    const data = await resp.json();
    if (data.url_pdf) {
      document.getElementById('visor').src = data.url_pdf;
    }
  } catch (err) {
    console.error('Error al mostrar estudio', err);
  }
}
