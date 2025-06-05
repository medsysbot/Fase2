document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('form-buscar-estudios');
  const listaFechas = document.getElementById('lista-fechas');
  const mensaje = document.getElementById('mensaje');
  const selectEstudio = document.getElementById('tipo_estudio');
  const inputDNI = document.getElementById('dni');
  const inputNombre = document.getElementById('nombre');

  // Lista ampliable de estudios (agregá los que quieras)
  const TIPOS_ESTUDIOS = [
    'Radiografía',
    'Ecografía',
    'Resonancia Magnética',
    'Tomografía',
    'Laboratorio',
    'Holter',
    'Electrocardiograma',
    'Endoscopía',
    'Mamografía',
    'Ergometría',
    'Colonoscopía',
    'Densitometría',
    'Test de Esfuerzo',
    'Biopsia',
    'Oftalmología',
    'Espirometría',
    'Audiometría',
    'Otro'
  ];

  // Cargar select con todos los estudios
  selectEstudio.innerHTML = '<option value="">Seleccione un tipo</option>';
  TIPOS_ESTUDIOS.forEach(t => {
    const op = document.createElement('option');
    op.value = t;
    op.textContent = t;
    selectEstudio.appendChild(op);
  });

  // Autocompletado de pacientes (puedes adaptar el endpoint según backend)
  inputDNI.addEventListener('input', autocompletarPacientes);
  inputNombre.addEventListener('input', autocompletarPacientes);

  async function autocompletarPacientes() {
    // Requiere al menos 2 caracteres en uno de los campos
    const qDNI = inputDNI.value.trim();
    const qNom = inputNombre.value.trim();
    if (qDNI.length < 2 && qNom.length < 2) return;

    // Podrías combinar ambos en la consulta si tu backend lo soporta
    try {
      const params = new URLSearchParams();
      if (qDNI.length >= 2) params.append("dni", qDNI);
      if (qNom.length >= 2) params.append("nombre", qNom);

      const resp = await fetch(`/api/sugerencias_pacientes?${params.toString()}`);
      const data = await resp.json();

      // Opcional: podés mostrar sugerencias en una datalist, o en inputs individuales
      // (La implementación depende del backend y el UX que quieras)
      // Si sólo querés autocompletar, podés adaptar esto fácilmente
    } catch (_) {
      // Sin acciones, sólo sugerencia opcional
    }
  }

  // Buscar estudios por paciente y tipo
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    listaFechas.innerHTML = '';
    mensaje.textContent = '';

    const dni = inputDNI.value.trim();
    const nombre = inputNombre.value.trim();
    const tipo_estudio = selectEstudio.value;

    if ((!dni && !nombre) || !tipo_estudio) {
      showAlert({
        mensaje: "Debe completar DNI o nombre y seleccionar tipo de estudio.",
        tipo: "info"
      });
      mensaje.textContent = "Debe completar DNI o nombre y seleccionar tipo de estudio.";
      return;
    }

    mensaje.textContent = "Buscando estudios...";
    try {
      // Ajusta el endpoint según tu backend
      const params = new URLSearchParams();
      if (dni) params.append('dni', dni);
      if (nombre) params.append('nombre', nombre);
      params.append('tipo_estudio', tipo_estudio);

      const resp = await fetch(`/consultar_estudios?${params.toString()}`);
      const data = await resp.json();
      const estudios = data.estudios || [];

      if (estudios.length === 0) {
        showAlert({
          mensaje: "No se encontraron estudios de este tipo para este paciente.",
          tipo: "info"
        });
        mensaje.textContent = "No se encontraron estudios de este tipo para este paciente.";
        return;
      }

      mensaje.textContent = "Hacé clic en la fecha para ver el estudio:";
      estudios.forEach((est) => {
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

  // Limpia resultados al resetear el form
  form.addEventListener('reset', () => {
    listaFechas.innerHTML = '';
    mensaje.textContent = "Ingrese DNI, nombre y seleccione un estudio para ver los resultados.";
  });
});
