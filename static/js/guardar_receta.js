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

function mostrarVistaPrevia(input, imgId, btnId) {
  const file = input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const img = document.getElementById(imgId);
    const btn = document.getElementById(btnId);
    img.src = e.target.result;
    img.style.display = 'block';
    btn.style.display = 'inline-block';
    input.style.display = 'none';
  };
  reader.readAsDataURL(file);
}

function eliminarImagen(inputId, imgId, btnId) {
  document.getElementById(inputId).value = '';
  const img = document.getElementById(imgId);
  const btn = document.getElementById(btnId);
  img.src = '';
  img.style.display = 'none';
  btn.style.display = 'none';
  document.getElementById(inputId).style.display = 'block';

  const formData = new FormData();
  formData.append('tipo', inputId);
  fetch('/eliminar_imagen_receta', { method: 'POST', body: formData });
}

async function obtenerEmailPorDni(dni) {
  try {
    const formData = new FormData();
    formData.append('dni', dni);
    const res = await fetch('/obtener_email_receta', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    return data.email || null;
  } catch (e) {
    console.error('Error al obtener email:', e);
    return null;
  }
}

async function enviarPorCorreo() {
  const nombre = document.getElementById('nombre').value.trim();
  const dni = document.getElementById('dni').value.trim();
  const email = await obtenerEmailPorDni(dni);

  if (!email) {
    showAlert('error', 'No se encontró un e-mail para este DNI.', false, 3000);
    return;
  }

  try {
    showAlert('email', 'Enviando e-mail…', false, 3000);
    await new Promise((r) => setTimeout(r, 3200));

    const formData = new FormData();
    formData.append('email', email);
    formData.append('nombre', nombre);
    formData.append('dni', dni);

    const response = await fetch('/enviar_pdf_receta', {
      method: 'POST',
      body: formData,
    });

    const resultado = await response.json();

    if (resultado.exito) {
      showAlert('suceso', 'E-mail enviado con éxito', false, 3000);
    } else {
      showAlert('error', 'Error al enviar el e-mail', false, 3000);
    }
  } catch (error) {
    console.error('Error al enviar:', error);
    showAlert('error', 'Error al enviar el e-mail', false, 3000);
  }
}

async function cargarFirmas() {
  try {
    const res = await fetch('/obtener_firma_sello');
    const data = await res.json();
    if (data.firma_url) {
      const img = document.getElementById('firma-preview');
      img.src = data.firma_url;
      img.style.display = 'block';
      document.getElementById('firma-delete').style.display = 'inline-block';
      document.getElementById('firma').style.display = 'none';
    }
    if (data.sello_url) {
      const img = document.getElementById('sello-preview');
      img.src = data.sello_url;
      img.style.display = 'block';
      document.getElementById('sello-delete').style.display = 'inline-block';
      document.getElementById('sello').style.display = 'none';
    }
  } catch (e) {
    console.error('Error al cargar firmas:', e);
  }
}

window.addEventListener('load', cargarFirmas);
