document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('form-buscar-estudios');
  const listaFechas = document.getElementById('lista-fechas');
  const mensaje = document.getElementById('mensaje');
  const visorPDFBox = document.getElementById('visor-pdf-box');
  const visorPDF = document.getElementById('visorPDF');
  const abrirPestaniaBtn = document.getElementById('abrir-nueva-pestania');

  let estudios = [];

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    listaFechas.innerHTML = '';
    mensaje.textContent = '';
    visorPDFBox.style.display = "none";
    visorPDF.src = '';
    abrirPestaniaBtn.style.display = "none";

    const paciente_id = form.paciente_id.value.trim();
    const tipo_estudio = form.tipo_estudio.value;

    if (!paciente_id || !tipo_estudio) {
      showAlert({
        mensaje: "Debe completar el DNI y seleccionar tipo de estudio.",
        tipo: "info"
      });
      mensaje.textContent = "Debe completar el DNI y seleccionar tipo de estudio.";
      return;
    }

    mensaje.textContent = "Buscando estudios...";
    try {
      // Modificá el endpoint según tu backend
      const resp = await fetch(`/consultar_estudios/${paciente_id}`);
      const data = await resp.json();
      estudios = data.estudios || [];

      // Filtra por tipo de estudio
      const filtrados = estudios.filter(est => est.tipo_estudio === tipo_estudio);

      if (filtrados.length === 0) {
        showAlert({
          mensaje: "No se encontraron estudios de este tipo para este paciente.",
          tipo: "info"
        });
        mensaje.textContent = "No se encontraron estudios de este tipo para este paciente.";
        return;
      }

      mensaje.textContent = "Seleccione la fecha del estudio que desea visualizar:";
      filtrados.forEach((est, i) => {
        const li = document.createElement('li');
        const btn = document.createElement('button');
        btn.className = 'fecha-link';
        btn.type = 'button';
        btn.innerHTML = `<span>${est.fecha || 'Sin fecha'} — ${est.descripcion || est.tipo_estudio}</span>`;
        btn.addEventListener('click', () => {
          document.querySelectorAll('.fecha-link').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          visorPDF.src = est.pdf_url;
          visorPDFBox.style.display = 'flex';
          abrirPestaniaBtn.style.display = 'inline-block';
          abrirPestaniaBtn.onclick = () => window.open(est.pdf_url, '_blank');
          showAlert({
            mensaje: "Mostrando estudio seleccionado.",
            tipo: "success"
          });
        });
        li.appendChild(btn);
        listaFechas.appendChild(li);
      });

    } catch (err) {
      showAlert({
        mensaje: "Error consultando los estudios. Intente de nuevo.",
        tipo: "error"
      });
      mensaje.textContent = "Error consultando los estudios. Intente de nuevo.";
    }
  });

  // Limpia visor si cambia búsqueda
  form.addEventListener('reset', () => {
    listaFechas.innerHTML = '';
    visorPDFBox.style.display = "none";
    visorPDF.src = '';
    mensaje.textContent = "Complete el DNI y seleccione tipo de estudio para ver los resultados disponibles.";
  });
});
