// ╔════════════════════════════════════╗
// ║      firma_sello.js      ║
// ╚════════════════════════════════════╝
async function cargarFirmas() {
  try {
    const res = await fetch('/obtener_firma_sello');
    const data = await res.json();
    if (data.firma_url) {
      const img = document.getElementById('firma-preview');
      img.src = data.firma_url;
      img.style.display = 'block';
      img.style.maxWidth = '100px';
      img.style.height = 'auto';
    }
    if (data.sello_url) {
      const img = document.getElementById('sello-preview');
      img.src = data.sello_url;
      img.style.display = 'block';
      img.style.maxWidth = '100px';
      img.style.height = 'auto';
    }
  } catch (e) {
    console.error('Error al cargar firmas:', e);
  }
}

window.addEventListener('load', cargarFirmas);
