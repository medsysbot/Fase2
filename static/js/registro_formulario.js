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

document.getElementById("btn-no").onclick = closeAlert;
document.getElementById("btn-borrar").onclick = function () {
  confirmarBorradoPaciente();
  closeAlert();
};

/*────────────────────────────────────*/
/*      FUNCIÓN: GUARDAR PACIENTE     */
/*────────────────────────────────────*/

async function guardarPDF() {
  const datos = {
    nombres: document.getElementById('nombres').value.trim(),
    apellido: document.getElementById('apellido').value.trim(),
    dni: document.getElementById('dni').value.trim(),
    fecha_nacimiento: document.getElementById('fecha_nacimiento').value,
    telefono: document.getElementById('telefono').value.trim(),
    email: document.getElementById('email').value.trim(),
    domicilio: document.getElementById('domicilio').value.trim(),
    obra_social: document.getElementById('obra_social').value.trim(),
    numero_afiliado: document.getElementById('numero_afiliado').value.trim(),
    contacto_emergencia: document.getElementById('contacto_emergencia').value.trim()
  };

  try {
    showAlert("guardado", "Guardando Paciente…", false, 3000);
    await new Promise(resolve => setTimeout(resolve, 3200));

    const formData = new FormData();
    for (const key in datos) {
      formData.append(key, datos[key]);
    }

    const response = await fetch('/generar_pdf_paciente', {
      method: 'POST',
      body: formData
    });

    const resultado = await response.json();

    if (resultado.exito && resultado.pdf_url) {
      showAlert("suceso", "Paciente Guardado Con Éxito", false, 3000);
      sessionStorage.setItem('pdfURL', resultado.pdf_url);
    } else if (resultado.mensaje) {
      showAlert("pacienteCargado", "El Paciente Ya Está Registrado", false, 3000);
    } else {
      showAlert("error", "Error Al Guardar El Paciente", false, 4000);
    }
  } catch (error) {
    console.error('Error al guardar:', error);
    showAlert("error", "Error Al Guardar El Paciente", false, 4000);
  }
}

/*──────────────────────────────────────────*/
/*      FUNCIÓN: ENVIAR PDF POR CORREO      */
/*──────────────────────────────────────────*/

async function enviarPorCorreo() {
  const nombres = document.getElementById('nombres').value.trim();
  const apellido = document.getElementById('apellido').value.trim();
  const email = document.getElementById('email').value.trim();

  if (!email) {
    showAlert("error", "El campo de correo electrónico está vacío.", false, 3000);
    return;
  }

  try {
    showAlert("email", "Enviando e-mail…", false, 3000);
    await new Promise(resolve => setTimeout(resolve, 3200));

    const formData = new FormData();
    formData.append("nombres", nombres);
    formData.append("apellido", apellido);
    formData.append("email", email);

    const response = await fetch('/enviar_pdf_paciente', {
      method: 'POST',
      body: formData
    });

    const resultado = await response.json();

    if (resultado.exito) {
      showAlert("suceso", "E-mail Enviado", false, 3000);
    } else {
      showAlert("error", "Error Al Enviar el E-mail", false, 3000);
    }
  } catch (error) {
    console.error('Error al enviar el e-mail:', error);
    showAlert("error", "Error Al Enviar el E-mail", false, 3000);
  }
}

/*────────────────────────────────────────*/
/*      FUNCIÓN: ABRIR PDF COMPATIBLE     */
/*────────────────────────────────────────*/

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

/*──────────────────────────────────────*/
/*      FUNCIÓN: MOSTRAR CONFIRMACIÓN   */
/*──────────────────────────────────────*/

function prepararBorradoPaciente() {
  showAlert("alerta", "Borrado De Paciente Definitivo ¿Desea Continuar?", true, "infinito");
}

/*──────────────────────────────────────*/
/*      FUNCIÓN: CANCELAR BORRADO       */
/*──────────────────────────────────────*/

function cancelarBorradoPaciente() {
  document.getElementById('confirmacion-borrado').style.display = 'none';
}

/*──────────────────────────────────────*/
/*      FUNCIÓN: CONFIRMAR BORRADO      */
/*──────────────────────────────────────*/

async function confirmarBorradoPaciente() {
  const dni = document.getElementById('dni').value.trim();

  if (!dni) {
    showAlert("error", "Debes ingresar un DNI válido.", false, 3000);
    return;
  }

  // Mostramos el cartel intermedio ANTES del fetch
  showAlert("borrado", "Borrando Paciente…", false, 3000);
  await new Promise(resolve => setTimeout(resolve, 3200));  // Esperamos que se vea

  try {
    const response = await fetch('/eliminar_paciente', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dni: dni })
    });

    const resultado = await response.json();

    if (resultado.exito || resultado.mensaje) {
      showAlert("suceso", "Paciente Borrado", false, 3000);
      document.getElementById('form-registro').reset();
      document.getElementById('confirmacion-borrado').style.display = 'none';
      sessionStorage.removeItem('pdfURL');
    } else {
      showAlert("error", "Error Al Borrar El Paciente", false, 3000);
    }
  } catch (error) {
    console.error('Error al eliminar:', error);
    showAlert("error", "Error Al Borrar El Paciente", false, 3000);
  }
}
