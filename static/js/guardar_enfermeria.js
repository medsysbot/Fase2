// ╔════════════════════════════════════╗
// ║      guardar_enfermeria.js        ║
// ╚════════════════════════════════════╝
async function guardarEnfermeria() {
  const form = document.getElementById('form-enfermeria');
  const formData = new FormData(form);

  try {
    showAlert('guardado', 'Guardando datos…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));

    const response = await fetch('/guardar_datos_enfermeria', {
      method: 'POST',
      body: formData
    });
    const resultado = await response.json();

    if (resultado.exito) {
      showAlert('suceso', 'Datos guardados', false, 3000);
    } else {
      showAlert('error', resultado.mensaje || 'Error al guardar', false, 4000);
    }
  } catch (error) {
    console.error('Error al guardar:', error);
    showAlert('error', 'Error al guardar', false, 4000);
  }
}
