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

function eliminarImagen(tipo, imgId, btnId) {
  document.getElementById(tipo).value = '';
  const img = document.getElementById(imgId);
  const btn = document.getElementById(btnId);
  img.src = '';
  img.style.display = 'none';
  btn.style.display = 'none';
  document.getElementById(tipo).style.display = 'block';

  const formData = new FormData();
  formData.append('tipo', tipo);
  fetch('/eliminar_firma_sello', { method: 'POST', body: formData });
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
