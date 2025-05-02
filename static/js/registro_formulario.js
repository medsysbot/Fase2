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
      alert("PDF generado y paciente guardado correctamente.");
    } else {
      alert("No se generó el PDF. Verificá los datos.");
    }
  })
  .catch(error => {
    console.error("Error al guardar:", error);
    alert("Ocurrió un problema al generar el PDF.");
  });
}

function imprimirPDF() {
  const iframe = document.getElementById('pdf-visor');
  if (iframe && iframe.contentWindow) {
    iframe.focus();
    iframe.contentWindow.print();
  } else {
    alert("No se pudo acceder al visor PDF.");
  }
}

function enviarPorCorreo() {
  const nombre = document.querySelector('[name="nombres"]').value.trim();
  const email = document.querySelector('[name="email"]').value.trim();
  if (!nombre || !email) {
    alert("Por favor, completá nombre y correo electrónico.");
    return;
  }
  document.getElementById("nombreOculto").value = nombre;
  document.getElementById("emailOculto").value = email;
  document.getElementById("form-enviar").submit();
  alert("El PDF se está enviando al correo del paciente...");
}
