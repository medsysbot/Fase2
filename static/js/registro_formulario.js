let campoActivo = null;

document.querySelectorAll("input").forEach((campo) => {
  campo.addEventListener("focus", () => {
    campoActivo = campo;
  });
});

function activarVoz() {
  if (!('webkitSpeechRecognition' in window)) {
    alert("Tu navegador no soporta reconocimiento de voz.");
    return;
  }
  const reconocimiento = new webkitSpeechRecognition();
  reconocimiento.lang = "es-ES";
  reconocimiento.interimResults = false;
  reconocimiento.maxAlternatives = 1;
  reconocimiento.onresult = function (evento) {
    const texto = evento.results[0][0].transcript;
    if (campoActivo) {
      campoActivo.value = texto;
    }
  };
  reconocimiento.onerror = function (evento) {
    console.error("Error de reconocimiento: ", evento.error);
  };
  reconocimiento.start();
}

async function guardarPDF() {
  const datos = {
    nombres: document.getElementById("nombres").value.trim(),
    apellido: document.getElementById("apellido").value.trim(),
    dni: document.getElementById("dni").value.trim(),
    fecha_nacimiento: document.getElementById("fecha_nacimiento").value.trim(),
    telefono: document.getElementById("telefono").value.trim(),
    email: document.getElementById("email").value.trim(),
    domicilio: document.getElementById("domicilio").value.trim(),
    obra_social: document.getElementById("obra_social").value.trim(),
    numero_afiliado: document.getElementById("numero_afiliado").value.trim(),
    contacto_emergencia: document.getElementById("contacto_emergencia").value.trim()
  };

  const formData = new FormData();
  Object.entries(datos).forEach(([clave, valor]) => formData.append(clave, valor));

  try {
    const response = await fetch("/generar_pdf_paciente", {
      method: "POST",
      body: formData
    });
    const data = await response.json();

    if (response.ok && data.url) {
      // Corrección doble barra en URL
      const urlCorregida = data.url.replace(/([^:]\/)\/+/g, "$1");
      document.getElementById("pdf-visor").src = urlCorregida;
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
  const src = iframe?.src;

  if (!src || src === "about:blank") {
    alert("No hay PDF cargado.");
    return;
  }

  // Abrir nueva ventana directamente con el PDF
  const nuevaVentana = window.open(src, "_blank");
  if (!nuevaVentana) {
    alert("No se pudo abrir la ventana para imprimir.");
    return;
  }

  // Esperar que cargue el PDF y luego activar impresión
  nuevaVentana.onload = () => {
    nuevaVentana.focus();
    nuevaVentana.print();
  };
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

  // Mostrar cartel central en vez de redirigir
  const cartel = document.createElement("div");
  cartel.textContent = "E-mail enviado exitosamente.";
  cartel.style.position = "fixed";
  cartel.style.top = "50%";
  cartel.style.left = "50%";
  cartel.style.transform = "translate(-50%, -50%)";
  cartel.style.backgroundColor = "#e0f7fa";
  cartel.style.padding = "20px";
  cartel.style.borderRadius = "10px";
  cartel.style.boxShadow = "0 0 10px rgba(0,0,0,0.2)";
  cartel.style.fontSize = "18px";
  cartel.style.fontWeight = "bold";
  document.body.appendChild(cartel);

  setTimeout(() => cartel.remove(), 3000);
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
