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
    const formData = new FormData();
    for (const key in datos) {
      formData.append(key, datos[key]);
    }

    showAlert("guardado", "Guardando paciente...");

    const response = await fetch('/generar_pdf_paciente', {
      method: 'POST',
      body: formData
    });

    const resultado = await response.json();

    closeAlert();

    if (resultado.exito && resultado.pdf_url) {
      showAlert('suceso', 'Paciente guardado exitosamente. PDF generado.');
      sessionStorage.setItem('pdfURL', resultado.pdf_url);
    } else if (resultado.mensaje) {
      showAlert('alerta', resultado.mensaje);
    } else {
      showAlert('error', 'Error desconocido al guardar el paciente.');
    }
  } catch (error) {
    console.error('Error al guardar:', error);
    closeAlert();
    showAlert('error', 'Error en el servidor.');
  }
}

// Función para enviar el PDF por correo
async function enviarPorCorreo() {
  const nombres = document.getElementById('nombres').value.trim();
  const apellido = document.getElementById('apellido').value.trim();
  const email = document.getElementById('email').value.trim();

  if (!email) {
    showAlert('alerta', 'El campo de correo electrónico está vacío.');
    return;
  }

  try {
    showAlert("guardado", "Enviando e-mail...");

    const formData = new FormData();
    formData.append("nombres", nombres);
    formData.append("apellido", apellido);
    formData.append("email", email);

    const response = await fetch('/enviar_pdf_paciente', {
      method: 'POST',
      body: formData
    });

    const resultado = await response.json();
    closeAlert();

    if (resultado.exito) {
      showAlert('suceso', 'E-mail enviado exitosamente.');
    } else {
      showAlert('error', 'No se pudo enviar el correo.');
    }
  } catch (error) {
    console.error('Error al enviar el e-mail:', error);
    closeAlert();
    showAlert('error', 'Error en el servidor al enviar el e-mail.');
  }
}

// Abrir el PDF en una nueva pestaña
function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL');
  if (url) {
    window.open(url, '_blank');
  } else {
    showAlert('pdf', 'No hay PDF disponible. Por favor, genera uno primero.');
  }
}

// Mostrar cartel de confirmación
function prepararBorradoPaciente() {
  document.getElementById('confirmacion-borrado').style.display = 'block';
}

// Ocultar cartel
function cancelarBorradoPaciente() {
  document.getElementById('confirmacion-borrado').style.display = 'none';
}

// Confirmar borrado con respaldo
async function confirmarBorradoPaciente() {
  const dni = document.getElementById('dni').value.trim();

  if (!dni) {
    showAlert('alerta', 'Debes ingresar un DNI válido.');
    return;
  }

  try {
    showAlert("borrado", "Eliminando paciente...");

    const response = await fetch('/eliminar_paciente', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dni: dni })
    });

    const resultado = await response.json();
    closeAlert();

    if (resultado.exito || resultado.mensaje) {
      showAlert('suceso', 'Paciente eliminado y respaldado correctamente.');
      document.getElementById('form-registro').reset();
      document.getElementById('confirmacion-borrado').style.display = 'none';
      sessionStorage.removeItem('pdfURL');
    } else {
      showAlert('error', 'No se pudo eliminar el paciente.');
    }
  } catch (error) {
    console.error('Error al eliminar:', error);
    closeAlert();
    showAlert('error', 'Error en el servidor al eliminar.');
  }
}
