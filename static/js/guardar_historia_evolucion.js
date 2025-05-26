// ╔════════════════════════════════════╗
// ║      guardar_historia_evolucion.js      ║
// ╚════════════════════════════════════╝
function guardarPDF() {
  const formData = new FormData(document.getElementById("form-evolucion"));

  fetch('/generar_pdf_evolucion', {
    method: 'POST',
    body: formData
  })
  .then(response => {
    if (response.ok) {
      alert('PDF generado correctamente');
      document.querySelector('.visor-pdf iframe').src = '/static/doc/historia-evolucion-diaria-generada.pdf?' + new Date().getTime();
    } else {
      alert('Error al generar el PDF. Intenta nuevamente.');
    }
  })
  .catch(error => {
    console.error("Error de conexión:", error);
    alert("No se pudo conectar con el servidor.");
  });
}