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
