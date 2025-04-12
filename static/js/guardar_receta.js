function guardarPDF() {
  const nombre = document.getElementById('nombre').value;
  const dni = document.getElementById('dni').value;
  const diagnostico = document.getElementById('diagnostico').value;
  const fecha = document.getElementById('fecha').value;
  const medicamentos = document.getElementById('medicamentos').value;

  if (!nombre || !dni || !diagnostico || !fecha || !medicamentos) {
    alert("Por favor, completá todos los campos antes de guardar.");
    return;
  }

  fetch('/generar-pdf-receta', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nombre, dni, diagnostico, fecha, medicamentos })
  })
  .then(response => {
    if (response.ok) {
      alert('PDF generado correctamente');
      document.querySelector('.visor-pdf iframe').src = '/static/doc/receta-medica-generada.pdf?' + new Date().getTime();
    } else {
      alert('Error al generar la receta. Intenta nuevamente.');
    }
  })
  .catch(error => {
    console.error("Error de conexión:", error);
    alert("No se pudo conectar con el servidor.");
  });
}
