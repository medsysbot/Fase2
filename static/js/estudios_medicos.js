document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('form-buscar-estudios');
  const listaFechas = document.getElementById('lista-fechas');
  const mensaje = document.getElementById('mensaje');
  const datalist = document.getElementById('pacientes-list');
  const inputPaciente = form.paciente_id;
  const selectEstudio = form.tipo_estudio;

  const TIPOS_ESTUDIOS = ['Radiografía', 'Ecografía', 'Resonancia', 'Laboratorio'];
  selectEstudio.innerHTML = '<option value="">Seleccione un tipo</option>';
  TIPOS_ESTUDIOS.forEach(t => {
    const op = document.createElement('option');
    op.value = t;
    op.textContent = t;
    selectEstudio.appendChild(op);
  });

  inputPaciente.addEventListener('input', async () => {
    const q = inputPaciente.value.trim();
    if (q.length < 2) return;
    try {
      const resp = await fetch(`/api/sugerencias_pacientes?q=${encodeURIComponent(q)}`);
      const data = await resp.json();
      datalist.innerHTML = '';
      (data.pacientes || []).forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.dni;
        opt.label = `${p.nombres} ${p.apellido}`;
        datalist.appendChild(opt);
      });
    } catch (_) {
      datalist.innerHTML = '';
    }
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    listaFechas.innerHTML = '';
    mensaje.textContent = '';

    const paciente_id = form.paciente_id.value.trim();
    const tipo_estudio = form.tipo_estudio.value;

    if (!paciente_id || !tipo_estudio) {
      showAlert({
        mensaje: "Debe completar el paciente y seleccionar tipo de estudio.",
        tipo: "info"
      });
      mensaje.textContent = "Debe completar el paciente y seleccionar tipo de estudio.";
      return;
    }

    mensaje.textContent = "Buscando estudios...";
    try {
      // Cambia el endpoint según tu backend si es necesario
      const resp = await fetch(`/consultar_estudios/${paciente_id}`);
      const data = await resp.json();
      const estudios = data.estudios || [];

      // Filtrar por tipo de estudio
      const filtrados = estudios.filter(est => est.tipo_estudio === tipo_estudio);

      if (filtrados.length === 0) {
        showAlert({
          mensaje: "No se encontraron estudios de este tipo para este paciente.",
          tipo: "info"
        });
        mensaje.textContent = "No se encontraron estudios de este tipo para este paciente.";
        return;
      }

      mensaje.textContent = "Hacé clic en la fecha para ver el estudio:";
      filtrados.forEach((est) => {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.className = 'fecha-link';
        a.href = est.pdf_url;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.textContent = `${est.fecha || 'Sin fecha'} — ${est.descripcion || est.tipo_estudio}`;
        li.appendChild(a);
        listaFechas.appendChild(li);
      });

      showAlert({
        mensaje: "Resultados listos. Abrí el estudio que quieras en nueva pestaña.",
        tipo: "success"
      });

    } catch (err) {
      showAlert({
        mensaje: "Error consultando los estudios. Intente de nuevo.",
        tipo: "error"
      });
      mensaje.textContent = "Error consultando los estudios. Intente de nuevo.";
    }
  });

  // Limpia resultados si resetean el form
  form.addEventListener('reset', () => {
    listaFechas.innerHTML = '';
    mensaje.textContent = "Complete el paciente y seleccione tipo de estudio para ver los resultados disponibles.";
  });
});
