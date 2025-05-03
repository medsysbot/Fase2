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

  try {
    const response = await fetch("/generar_pdf_paciente", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (data.url && data.url.includes(".pdf")) {
      const visor = document.getElementById("pdf-visor");
      visor.src = data.url;
      alert("Paciente guardado y PDF generado con éxito.");
    } else {
      alert("No se pudo mostrar el PDF. Verifica permisos en Supabase y que el archivo se haya subido correctamente.");
    }
  } catch (error) {
    alert("Error al guardar el paciente: " + error.message);
  }
}
