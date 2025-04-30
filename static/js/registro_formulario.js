function guardarPDF() {
  const form = document.getElementById("form-registro");
  const formData = new FormData(form);

  fetch("/generar_pdf_paciente", {
    method: "POST",
    body: formData,
  })
  .then(response => response.json())
  .then(data => {
    if (data.filename) {
      const visor = document.getElementById("pdf-visor");
      visor.src = `/static/doc/${data.filename}?t=${new Date().getTime()}`;
      alert("PDF generado correctamente.");
    } else {
      alert("Error al generar el PDF.");
    }
  })
  .catch(error => {
    console.error("Error al guardar:", error);
    alert("Hubo un problema al guardar el PDF.");
  });
}
