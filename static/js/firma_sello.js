// ╔════════════════════════════════════╗
// ║      firma_sello.js      ║
// ╚════════════════════════════════════╝
async function mostrarVistaPrevia(input, imgId, btnId, tipo) {
  const file = input.files[0];
  if (!file) return;
  if (!file.type.match(/image\/png/)) {
    showAlert("error", "Solo se permiten archivos PNG.", false, 3000);
    input.value = "";
    return;
  }
  const reader = new FileReader();
  reader.onload = async (e) => {
    const img = document.getElementById(imgId);
    const btn = document.getElementById(btnId);
    img.src = e.target.result;
    img.style.display = 'block';
    img.style.maxWidth = '150px';
    img.style.height = 'auto';
    btn.style.display = 'inline-block';
    input.style.display = 'none';

    const formData = new FormData();
    formData.append('tipo', tipo);
    formData.append('archivo', file);
    try {
      await fetch('/subir_firma_sello', {
        method: 'POST',
        body: formData,
      });
    } catch (e) {
      console.error('Error al subir imagen:', e);
    }
  };
  reader.readAsDataURL(file);
}

async function eliminarImagen(tipo, imgId, btnId) {
  const formData = new FormData();
  formData.append('tipo', tipo);
  try {
    await fetch('/eliminar_firma_sello', {
      method: 'POST',
      body: formData,
    });
  } catch (e) {
    console.error('Error al eliminar imagen:', e);
  }
  document.getElementById(tipo).value = '';
  const img = document.getElementById(imgId);
  const btn = document.getElementById(btnId);
  img.src = '';
  img.style.display = 'none';
  btn.style.display = 'none';
  document.getElementById(tipo).style.display = 'block';
}

async function cargarFirmas() {
  try {
    const res = await fetch('/obtener_firma_sello');
    const data = await res.json();
    if (data.firma_url) {
      const img = document.getElementById('firma-preview');
      img.src = data.firma_url;
      img.style.display = 'block';
      img.style.maxWidth = '150px';
      img.style.height = 'auto';
      document.getElementById('firma-delete').style.display = 'inline-block';
      document.getElementById('firma').style.display = 'none';
    }
    if (data.sello_url) {
      const img = document.getElementById('sello-preview');
      img.src = data.sello_url;
      img.style.display = 'block';
      img.style.maxWidth = '150px';
      img.style.height = 'auto';
      document.getElementById('sello-delete').style.display = 'inline-block';
      document.getElementById('sello').style.display = 'none';
    }
  } catch (e) {
    console.error('Error al cargar firmas:', e);
  }
}

window.addEventListener('load', cargarFirmas);
