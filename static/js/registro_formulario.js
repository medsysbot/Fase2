async function guardarPDF() {
  const nombres = document.getElementById("nombres").value.trim();
  const apellido = document.getElementById("apellido").value.trim();
  const dni = document.getElementById("dni").value.trim();
  const fecha_nacimiento = document.getElementById("fecha_nacimiento").value.trim();
  const telefono = document.getElementById("telefono").value.trim();
  const email = document.getElementById("email").value.trim();
  const domicilio = document.getElementById("domicilio").value.trim();
  const obra_social = document.getElementById("obra_social").value.trim();
  const numero_afiliado = document.getElementById("numero_afiliado").value.trim();
  const contacto_emergencia = document.getElementById("contacto_emergencia").value.trim();

  const formData = new FormData();
  formData.append("nombres", nombres);
  formData.append("apellido", apellido);
  formData.append("dni", dni);
  formData.append("fecha_nacimiento", fecha_nacimiento);
  formData.append("telefono", telefono);
  formData.append("email", email);
  formData.append("domicilio", domicilio);
  formData.append("obra_social", obra_social);
  formData.append("numero_afiliado", numero_afiliado);
  formData.append("contacto_emergencia", contacto_emergencia);

  try {
    const response = await fetch("/generar_pdf_paciente", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (response.ok && data.url) {
      document.getElementById("pdf-visor").src = data.url;
      alert("Paciente guardado y PDF generado con éxito.");
    } else {
      alert(data.mensaje || "No se pudo generar el PDF: " + (data.error || "Error desconocido."));
    }
  } catch (error) {
    alert("Error al guardar el paciente: " + error.message);
  }
}

function imprimirPDF() {
  const iframe = document.getElementById("pdf-visor");
  if (iframe && iframe.contentWindow) {
    iframe.contentWindow.focus();
    iframe.contentWindow.print();
  } else {
    alert("No se pudo acceder al visor PDF.");
  }
}

function enviarPorCorreo() {
  const nombre = document.getElementById("nombres").value.trim();
  const apellido = document.getElementById("apellido").value.trim();
  const email = document.getElementById("email").value.trim();

  if (!nombre || !apellido || !email) {
    alert("Por favor, completá nombre, apellido y correo electrónico.");
    return;
  }

  const formEnviar = document.createElement("form");
  formEnviar.method = "POST";
  formEnviar.action = "/enviar_pdf_paciente";

  formEnviar.innerHTML = `
    <input type="hidden" name="nombres" value="${nombre}">
    <input type="hidden" name="apellido" value="${apellido}">
    <input type="hidden" name="email" value="${email}">
  `;

  document.body.appendChild(formEnviar);
  formEnviar.submit();
  alert("El PDF se está enviando al correo del paciente...");
}

function prepararBorradoPaciente() {
  document.getElementById("confirmacion-borrado").style.display = "block";
}

function cancelarBorradoPaciente() {
  document.getElementById("confirmacion-borrado").style.display = "none";
}

function confirmarBorradoPaciente() {
  const dni = document.getElementById("dni").value.trim();
  if (!dni) {
    alert("Primero debes completar el DNI");
    return;
  }

  fetch("/eliminar-paciente", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dni })
  })
  .then(res => res.json())
  .then(res => {
    alert(res.message || "Paciente eliminado con respaldo");
    document.getElementById("confirmacion-borrado").style.display = "none";
    document.getElementById("form-registro").reset();
    document.getElementById("pdf-visor").src = "";
  })
  .catch(err => {
    alert("Error al eliminar paciente");
    console.error(err);
  });
}
