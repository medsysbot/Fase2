// ╔════════════════════════════════════╗
// ║      guardar_busqueda.js      ║
// ╚════════════════════════════════════╝
document.addEventListener("DOMContentLoaded", function () {
  const botonGuardar = document.querySelector("button[title='Guardar']");
  const botonEnviar = document.querySelector("button[title='Enviar']");
  const botonVerPdf = document.querySelector("button[title='Ver PDF']");

  async function ejecutarBusqueda() {
    const dni = document.getElementById("busqueda")?.value.trim();

    if (!dni) {
      showAlert("error", "Por favor, ingrese un DNI válido.", false, 3000);
      return;
    }

    try {
      showAlert("guardado", "Generando PDF…", false, 3000);
      await new Promise(r => setTimeout(r, 3200));

      const formData = new FormData();
      formData.append('dni', dni);
      const response = await fetch("/buscar_paciente", {
        method: "POST",
        body: formData
      });
      const resultado = await response.json();

      if (response.ok && resultado.exito) {
        const datos = resultado.datos || {};
        if (resultado.pdf_url) {
          sessionStorage.setItem('pdfURL_busqueda', resultado.pdf_url);
        }
        document.getElementById('res-nombre').textContent = datos.nombres || '-';
        document.getElementById('res-apellido').textContent = datos.apellido || '-';
        document.getElementById('res-telefono').textContent = datos.telefono || '-';
        document.getElementById('res-email').textContent = datos.email || '-';
        showAlert("suceso", "Paciente encontrado", false, 3000);
      } else {
        showAlert("error", resultado.mensaje || "Paciente no encontrado", false, 4000);
      }
    } catch (error) {
      console.error("Error:", error);
      showAlert("error", "Error al conectar con el servidor", false, 4000);
    }
  }

  if (botonGuardar) {
    botonGuardar.addEventListener("click", ejecutarBusqueda);
  }
  if (botonEnviar) {
    botonEnviar.addEventListener("click", enviarPorCorreo);
  }
  if (botonVerPdf) {
    botonVerPdf.addEventListener("click", abrirPDF);
  }
});

function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL_busqueda');
  if (url) {
    showAlert("cargaPDF", "Cargando PDF…", false, 3000);
    const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
    setTimeout(() => {
      if (isIOS) {
        window.location.href = url;
      } else {
        window.open(url, '_blank');
      }
    }, 1000);
  } else {
    showAlert("pdf", "Error Al Cargar El PDF", false, 3000);
  }
}

async function enviarPorCorreo() {
  const dni = document.getElementById('busqueda').value.trim();
  const pdfURL = sessionStorage.getItem('pdfURL_busqueda');
  if (!dni || !pdfURL) {
    showAlert('error', 'Debe realizar la búsqueda primero.', false, 3000);
    return;
  }

  try {
    showAlert('email', 'Enviando e-mail…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));
    const formData = new FormData();
    formData.append('dni', dni);
    formData.append('pdf_url', pdfURL);
    const response = await fetch('/enviar_pdf_busqueda', {
      method: 'POST',
      body: formData
    });
    const resultado = await response.json();
    if (resultado.exito) {
      showAlert('suceso', 'E-mail enviado con éxito', false, 3000);
    } else {
      showAlert('error', resultado.mensaje || 'Error al enviar el e-mail', false, 3000);
    }
  } catch (error) {
    console.error('Error al enviar:', error);
    showAlert('error', 'Error al enviar el e-mail', false, 3000);
  }
}
