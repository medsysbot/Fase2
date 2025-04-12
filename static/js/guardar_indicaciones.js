function guardarPDF() {
  const nombre = document.getElementById('nombre').value;
  const dni = document.getElementById('dni').value;
  const fecha = document.getElementById('fecha').value;
  const indicaciones = document.getElementById('indicaciones').value;

  if (!nombre || !dni || !fecha || !indicaciones) {
    alert("Por favor, completá todos los campos antes de guardar.");
    return;
  }

  fetch('/generar-pdf-indicaciones', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nombre, dni, fecha, indicaciones })
  })
  .then(response => {
    if (response.ok) {
      alert('PDF generado correctamente');
      document.querySelector('.visor-pdf iframe').src = '/static/doc/indicaciones-medicas-generado.pdf?' + new Date().getTime();
    } else {
      alert('Error al generar las indicaciones. Intenta nuevamente.');
    }
  })
  .catch(error => {
    console.error("Error de conexión:", error);
    alert("No se pudo conectar con el servidor.");
  });
}
