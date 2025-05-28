// ╔════════════════════════════════════╗
// ║      guardar_busqueda.js      ║
// ╚════════════════════════════════════╝
document.addEventListener("DOMContentLoaded", function () {
  const botonGuardar = document.querySelector("button[title='Guardar']");

  if (botonGuardar) {
    botonGuardar.addEventListener("click", async function () {
      const busqueda = document.getElementById("busqueda")?.value.trim();

      if (!busqueda) {
        showAlert("error", "Por favor, ingrese un nombre o DNI antes de guardar.", false, 3000);
        return;
      }

      try {
        showAlert("guardado", "Buscando…", false, 3000);
        await new Promise(r => setTimeout(r, 3200));

        const formData = new FormData();
        formData.append('dni', busqueda);
        const response = await fetch("/buscar_paciente", {
          method: "POST",
          body: formData
        });
        const resultado = await response.json();

        if (response.ok && resultado.pdf_url) {
          sessionStorage.setItem('pdfURL_busqueda', resultado.pdf_url);
          document.getElementById('pdf-visor').src = resultado.pdf_url;
          showAlert("suceso", "Búsqueda guardada", false, 3000);
        } else {
          showAlert("error", resultado.mensaje || "Error al generar el PDF", false, 4000);
        }
      } catch (error) {
        console.error("Error:", error);
        showAlert("error", "Error al conectar con el servidor", false, 4000);
      }
    });
  }
});

function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL_busqueda');
  if (url) {
    window.open(url, '_blank');
  } else {
    showAlert('pdf', 'Error al cargar el PDF', false, 3000);
  }
}
