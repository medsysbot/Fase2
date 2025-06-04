// ╔═══════════════════════════════════╗
// ║   enfermeria.js                   ║
// ╚═══════════════════════════════════╝
async function guardarEnfermeria() {
  const form = document.getElementById('form-enfermeria');
  const formData = new FormData(form);
  formData.set('institucion_id', sessionStorage.getItem('institucion_id') || '');
  formData.set('usuario_id', sessionStorage.getItem('usuario_id') || '');

  const campos = [
    'nombre', 'apellido', 'dni', 'edad', 'altura', 'peso', 'hora',
    'temperatura', 'glucemia', 'glasgow', 'saturacion', 'frecuencia_cardiaca',
    'ta', 'tad', 'dolor', 'triaje', 'motivo_consulta', 'profesional'
  ];
  for (const c of campos) {
    const valor = form.querySelector(`[name="${c}"]`).value.trim();
    if (!valor) {
      showAlert('error', 'Completa todos los campos.', false, 3000);
      return;
    }
  }

  try {
    showAlert('guardado', 'Guardando datos…', false, 3000);
    await new Promise(r => setTimeout(r, 3200));

    const resp = await fetch('/guardar_enfermeria', {
      method: 'POST',
      body: formData
    });
    const resultado = await resp.json();

    if (resp.ok) {
      showAlert('suceso', 'Datos guardados', false, 3000);
    } else {
      showAlert('error', resultado.error || 'Error al guardar', false, 4000);
    }
  } catch (e) {
    console.error('Error al guardar:', e);
    showAlert('error', 'Error al guardar', false, 4000);
  }
}

