function guardarPDF() {
  const formData = new FormData(document.getElementById("form-historia"));

  fetch('/generar-pdf-historia-clinica-completa', {
    method: 'POST',
    body: formData
  })
  .then(response => {
    if (response.ok) {
      alert('PDF generado correctamente');
      document.querySelector('.visor-pdf iframe').src = '/static/doc/historia-clinica-completa-generada.pdf?' + new Date().getTime();
    } else {
      alert('Error al generar el PDF. Intenta nuevamente.');
    }
  })
  .catch(error => {
    console.error("Error de conexión:", error);
    alert("No se pudo conectar con el servidor.");
  });
}