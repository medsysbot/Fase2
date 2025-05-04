// Supabase
const supabase = supabase.createClient(
  'https://wolcdduoroiobtadbcup.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' // tu clave service_role si lo requiere
);

// Función para guardar y generar PDF
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
    const response = await fetch('/guardar_paciente', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(datos)
    });

    const resultado = await response.json();
    if (resultado.exito && resultado.pdf_url) {
      alert('Paciente guardado con éxito. PDF generado con éxito.');
      sessionStorage.setItem('pdfURL', resultado.pdf_url);
    } else {
      alert('Error al guardar paciente o generar PDF.');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error en el servidor.');
  }
}

// Función para enviar el PDF por correo
async function enviarPorCorreo() {
  const dni = document.getElementById('dni').value.trim();
  try {
    const response = await fetch(`/enviar_correo/${dni}`, {
      method: 'POST'
    });
    const resultado = await response.json();
    if (resultado.exito) {
      alert('E-mail enviado exitosamente.');
    } else {
      alert('Error al enviar el e-mail.');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error en el envío.');
  }
}

// Función para redirigir al PDF
function abrirPDF() {
  const url = sessionStorage.getItem('pdfURL');
  if (url) {
    window.open(url, '_blank');
  } else {
    alert('No hay PDF disponible.');
  }
}

// Función de confirmación de borrado
function prepararBorradoPaciente() {
  const cartel = document.getElementById('confirmacion-borrado');
  cartel.style.display = 'block';
}

// Cancelar borrado
function cancelarBorradoPaciente() {
  document.getElementById('confirmacion-borrado').style.display = 'none';
}

// Confirmar y ejecutar borrado
async function confirmarBorradoPaciente() {
  const dni = document.getElementById('dni').value.trim();
  try {
    const response = await fetch(`/eliminar_paciente/${dni}`, {
      method: 'DELETE'
    });
    const resultado = await response.json();
    if (resultado.exito) {
      alert('Paciente eliminado con respaldo.');
      document.getElementById('form-registro').reset();
      document.getElementById('confirmacion-borrado').style.display = 'none';
      sessionStorage.removeItem('pdfURL');
    } else {
      alert('No se pudo eliminar el paciente.');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error en el servidor.');
  }
}
