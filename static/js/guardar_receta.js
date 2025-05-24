async function guardarPDF() {
  const form = document.getElementById("form-receta");
  const formData = new FormData(form);

  const firma = document.getElementById("firma");
  const sello = document.getElementById("sello");

  if (firma && firma.files.length > 0) {
    formData.append("firma", firma.files[0]);
  }
  if (sello && sello.files.length > 0) {
    formData.append("sello", sello.files[0]);
  }

  try {
    showAlert("guardado", "Guardando receta…", false, 3000);
    await new Promise(resolve => setTimeout(resolve, 3200));

    const response = await fetch('/generar_pdf_receta', {
      method: 'POST',
      body: formData
    });

    const resultado = await response.json();

    if (resultado.exito && resultado.pdf_url) {
      showAlert("suceso", "Receta guardada", false, 3000);
      sessionStorage.setItem('pdfURL', resultado.pdf_url);
    } else {
      showAlert("error", resultado.mensaje || "Error al guardar la receta", false, 4000);
    }
  } catch (error) {
    console.error('Error al guardar:', error);
    showAlert("error", "Error al guardar la receta", false, 4000);
  }
}

function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL');
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
