// Función para imprimir el PDF del visor
function imprimirPDF() {
  const iframe = document.querySelector('iframe');
  if (iframe && iframe.contentWindow) {
    iframe.contentWindow.focus();
    iframe.contentWindow.print();
  } else {
    alert("No se encontró el documento PDF para imprimir.");
  }
}

// Función para eliminar el PDF del visor
function eliminarPDF() {
  const visor = document.querySelector('iframe');
  if (visor) {
    visor.setAttribute('src', '');
    alert("PDF eliminado del visor.");
  } else {
    alert("No se encontró visor de PDF.");
  }
}

// Función para enviar un formulario (requiere ID)
function enviarFormulario(formId) {
  const form = document.getElementById(formId);
  if (form) {
    form.submit();
  } else {
    alert("Formulario no encontrado.");
  }
}

// Función simulada de guardado simple
function guardarPDF() {
  alert("Guardado correctamente.");
}

// Función de eliminación con confirmación
function confirmarEliminacionPDF() {
  const confirmar = confirm("¿Seguro que deseas eliminar este archivo?");
  if (confirmar) {
    eliminarPDF();
  }
}
