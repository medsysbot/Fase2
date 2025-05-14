/*──────────────────────────────*/
/*      ALERTAS PERSONALIZADAS  */
/*──────────────────────────────*/

function showAlert(type, message, withButtons = false, duration = 3000) {
  const iconos = {
    alerta: "/static/icons/alerta/alerta-alerta.png",
    borrado: "/static/icons/alerta/alerta-borrado.png",
    busqueda: "/static/icons/alerta/alerta-busqueda.png",
    error: "/static/icons/alerta/alerta-error.png",
    guardado: "/static/icons/alerta/alerta-guardado.png",
    suceso: "/static/icons/alerta/alerta-suceso.png",
    pacienteCargado: "/static/icons/alerta/alerta-paciente-cargado.png",
    pdf: "/static/icons/alerta/alerta-pdf.png",
    email: "/static/icons/alerta/alerta-email.png",
    cargaPDF: "/static/icons/alerta/alerta-carga-pdf.png"
  };

  const icono = document.getElementById("alert-icon");
  const texto = document.getElementById("alert-text");
  const botones = document.getElementById("alert-buttons");
  const contenedor = document.getElementById("alert-manager");

  icono.src = iconos[type] || iconos["alerta"];
  texto.textContent = message;
  botones.style.display = withButtons ? "flex" : "none";
  contenedor.style.display = "flex";

  if (!withButtons && duration !== "infinito") {
    setTimeout(() => {
      contenedor.style.display = "none";
    }, duration);
  }
}

function closeAlert() {
  document.getElementById("alert-manager").style.display = "none";
}

/*──────────────────────────────────────────────*/
/*    GUARDAR HISTORIA CLÍNICA Y GENERAR PDF    */
/*──────────────────────────────────────────────*/

async function guardarPDF() {
  const form = document.getElementById("form-historia");
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
  showAlert("guardado", "Guardando Historia Clínica…", false, 3000);
  await new Promise(resolve => setTimeout(resolve, 3200));

  const response = await fetch('/generar_pdf_historia_completa', {
    method: 'POST',
    body: formData
  });

  const resultado = await response.json();

  if (resultado.exito && resultado.pdf_url) {
    showAlert("suceso", "Historia Clínica Guardada", false, 3000);
    sessionStorage.setItem('pdfURL', resultado.pdf_url);
  } else if (resultado.mensaje && resultado.mensaje.toLowerCase().includes("registrada")) {
    showAlert("pacienteCargado", "La Historia Clínica Ya Está Registrada", false, 3000);
  } else {
    showAlert("error", resultado.mensaje || "Error Al Guardar Historia Clínica", false, 4000);
  }

} catch (error) {
  console.error('Error al guardar:', error);
  showAlert("error", "Error Al Guardar Historia Clínica", false, 4000);
}
  
    

/*──────────────────────────────────────────────*/
/*         ENVIAR HISTORIA POR CORREO           */
/*──────────────────────────────────────────────*/

async function enviarPorCorreo() {
  const form = document.getElementById("form-historia");

  const email = form.querySelector('[name="email"]')?.value.trim() || "";
  const nombre = form.querySelector('[name="nombre"]')?.value.trim() || "";
  const dni = form.querySelector('[name="dni"]')?.value.trim() || "";

  if (!email) {
    showAlert("error", "El campo de correo está vacío.", false, 3000);
    return;
  }

  try {
    showAlert("email", "Enviando e-mail…", false, 3000);
    await new Promise(resolve => setTimeout(resolve, 3200));

    const formData = new FormData();
    formData.append("email", email);
    formData.append("nombre", nombre);
    formData.append("dni", dni);

    const response = await fetch('/enviar_pdf_historia_completa', {
      method: 'POST',
      body: formData
    });

    const resultado = await response.json();

    if (resultado.exito) {
      showAlert("suceso", "E-mail enviado con éxito", false, 3000);
    } else {
      showAlert("error", "Error al enviar el e-mail", false, 3000);
    }
  } catch (error) {
    console.error('Error al enviar:', error);
    showAlert("error", "Error al enviar el e-mail", false, 3000);
  }
}

/*──────────────────────────────────────────────*/
/*             ABRIR PDF GUARDADO               */
/*──────────────────────────────────────────────*/

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
