async function subirArchivo(tipo) {
  const input = document.getElementById(tipo);
  if (!input.files.length) {
    alert('Seleccione un archivo');
    return;
  }
  const formData = new FormData();
  formData.append('tipo', tipo);
  formData.append('archivo', input.files[0]);
  try {
    const res = await fetch('/subir_firma_sello', {
      method: 'POST',
      body: formData,
    });
    if (res.ok) {
      alert('Imagen subida correctamente');
      window.location.reload();
    } else {
      const data = await res.json();
      alert(data.mensaje || 'Error al subir');
    }
  } catch (e) {
    alert('Error de red');
  }
}
