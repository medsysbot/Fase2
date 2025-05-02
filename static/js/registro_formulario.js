const supabase = supabase.createClient(
  'https://wolcdduoroiobtadbcup.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndvbGNkZHVvcm9pb2J0YWRiY3VwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYyMDE0OTMsImV4cCI6MjA2MTc3NzQ5M30.rV_1sa8iM8s6eCD-5m_wViCgWpd0d2xRHA_zQxRabHU'
);

async function guardarPDF() {
  const nombres = document.getElementById("nombres").value;
  const apellido = document.getElementById("apellido").value;
  const dni = document.getElementById("dni").value;
  const fecha_nacimiento = document.getElementById("fecha_nacimiento").value;
  const telefono = document.getElementById("telefono").value;
  const email = document.getElementById("email").value;
  const domicilio = document.getElementById("domicilio").value;
  const obra_social = document.getElementById("obra_social").value;
  const numero_afiliado = document.getElementById("numero_afiliado").value;
  const contacto_emergencia = document.getElementById("contacto_emergencia").value;

  const { data, error } = await supabase
    .from('pacientes')
    .insert([
      {
        nombres,
        apellido,
        dni,
        fecha_nacimiento,
        telefono,
        email,
        domicilio,
        obra_social,
        numero_afiliado,
        contacto_emergencia,
        institucion_id: 1
      }
    ])
    .select();

  if (error) {
    alert("Error al guardar en Supabase: " + error.message);
    return;
  }

  const formData = new FormData();
  formData.append('nombres', nombres);
  formData.append('apellido', apellido);
  formData.append('dni', dni);
  formData.append('fecha_nacimiento', fecha_nacimiento);
  formData.append('telefono', telefono);
  formData.append('email', email);
  formData.append('domicilio', domicilio);
  formData.append('obra_social', obra_social);
  formData.append('numero_afiliado', numero_afiliado);
  formData.append('contacto_emergencia', contacto_emergencia);

  fetch("/generar_pdf_paciente", {
    method: "POST",
    body: formData,
  })
  .then(response => response.json())
  .then(data => {
    if (data.filename) {
      document.getElementById("pdf-visor").src = `/static/doc/${data.filename}?t=${Date.now()}`;
      alert("PDF generado y paciente guardado correctamente.");
    } else {
      alert("No se generó el PDF. Verifica los datos.");
    }
  })
  .catch(error => {
    alert("Error al generar el PDF: " + error);
  });
}

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
  const nombre = document.getElementById('nombres').value.trim();
  const apellido = document.getElementById('apellido').value.trim();
  const email = document.getElementById('email').value.trim();

  if (!nombre || !apellido || !email) {
    alert("Por favor, completá nombre, apellido y correo electrónico.");
    return;
  }

  const formEnviar = document.createElement('form');
  formEnviar.method = 'POST';
  formEnviar.action = '/enviar_pdf_paciente';

  formEnviar.innerHTML = `
    <input type="hidden" name="nombres" value="${nombre}">
    <input type="hidden" name="apellido" value="${apellido}">
    <input type="hidden" name="email" value="${email}">
  `;

  document.body.appendChild(formEnviar);
  formEnviar.submit();
  alert("El PDF se está enviando al correo del paciente...");
}
