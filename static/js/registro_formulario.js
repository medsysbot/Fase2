// Función para guardar y generar el PDF del paciente
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
    showAlert("guardado", "Guardando paciente...");

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
      showAlert("suceso", "Paciente guardado exitosamente.");
      sessionStorage.setItem('pdfURL', resultado.pdf_url);
    } else if (resultado.mensaje) {
      showAlert("error", resultado.mensaje);
    } else {
      showAlert("error", "Error desconocido al guardar el paciente.");
    }
  } catch (error) {
    console.error('Error al guardar:', error);
    showAlert("error", "Error en el servidor.");
  }
}

// Función para enviar el PDF por correo
async function enviarPorCorreo() {
  const nombres = document.getElementById('nombres').value.trim();
  const apellido = document.getElementById('apellido').value.trim();
  const email = document.getElementById('email').value.trim();

  if (!email) {
    showAlert("error", "El campo de correo electrónico está vacío.");
    return;
  }

  try {
    showAlert("alerta", "Enviando e-mail...");

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
      showAlert("suceso", "E-mail enviado exitosamente.");
    } else {
      showAlert("error", "No se pudo enviar el correo.");
    }
  } catch (error) {
    console.error('Error al enviar el e-mail:', error);
    showAlert("error", "Error en el servidor al enviar el e-mail.");
  }
}

// Abrir el PDF en una nueva pestaña
function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL');
  if (url) {
    window.open(url, '_blank');
  } else {
    showAlert("pdf", "No hay PDF disponible.");
  }
}

// Mostrar cartel de confirmación
function prepararBorradoPaciente() {
  showAlert("borrado", "¿Desea borrar este paciente?", true);
}

// Ocultar cartel clásico (solo por si estuviera activo)
function cancelarBorradoPaciente() {
  document.getElementById('confirmacion-borrado').style.display = 'none';
}

// Confirmar borrado con respaldo
async function confirmarBorradoPaciente() {
  const dni = document.getElementById('dni').value.trim();

  if (!dni) {
    showAlert("error", "Debes ingresar un DNI válido.");
    return;
  }

  try {
    showAlert("borrado", "Borrando paciente...");

    const response = await fetch('/eliminar_paciente', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dni: dni })
    });

    const resultado = await response.json();
    if (resultado.exito || resultado.mensaje) {
      showAlert("suceso", "Paciente eliminado correctamente.");
      document.getElementById('form-registro').reset();
      document.getElementById('confirmacion-borrado').style.display = 'none';
      sessionStorage.removeItem('pdfURL');
    } else {
      showAlert("error", "No se pudo eliminar el paciente.");
    }
  } catch (error) {
    console.error('Error al eliminar:', error);
    showAlert("error", "Error en el servidor al eliminar.");
  }
}
