// buscar_paciente.js

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('form-busqueda-paciente');
  const resultados = document.getElementById('resultados-busqueda');
  const acciones = document.getElementById('acciones-busqueda');
  const emailEnvio = document.getElementById('email-envio-container');
  const verPdfBtn = document.getElementById('ver-pdf');
  const enviarPdfBtn = document.getElementById('enviar-pdf');
  const confirmarEnvioBtn = document.getElementById('confirmar-envio');
  const borrarBtn = document.getElementById('borrar-paciente');
  let resultadoActual = null;

  function iconoEstado(ok) {
    return ok ? '✅' : '❌';
  }

  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    resultados.style.display = 'none';
    acciones.style.display = 'none';
    emailEnvio.style.display = 'none';
    document.getElementById('hc-completa-icon').textContent = '⏳';
    document.getElementById('hc-resumida-icon').textContent = '⏳';
    document.getElementById('hc-diaria-icon').textContent = '⏳';
    document.getElementById('recetas-icon').textContent = '⏳';
    document.getElementById('turnos-icon').textContent = '⏳';
    document.getElementById('estudios-icon').textContent = '⏳';
    const dni = document.getElementById('dni-paciente').value;
    try {
      const res = await fetch('/api/buscar_paciente', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({dni})
      });
      const data = await res.json();
      resultadoActual = data;
      document.getElementById('hc-completa-icon').textContent = iconoEstado(data.historia_clinica_completa);
      document.getElementById('hc-resumida-icon').textContent = iconoEstado(data.historia_clinica_resumida);
      document.getElementById('hc-diaria-icon').textContent = iconoEstado(data.consulta_diaria);
      document.getElementById('recetas-icon').textContent = iconoEstado(data.recetas);
      document.getElementById('turnos-icon').textContent = iconoEstado(data.turnos);
      document.getElementById('estudios-icon').textContent = iconoEstado(data.estudios);
      resultados.style.display = 'block';
      if (
        data.historia_clinica_completa || data.historia_clinica_resumida ||
        data.consulta_diaria || data.recetas ||
        data.turnos || data.estudios
      ) {
        acciones.style.display = 'block';
      } else {
        acciones.style.display = 'none';
      }
    } catch (err) {
      alert('Error en la búsqueda. Reintente.');
    }
  });

  verPdfBtn.addEventListener('click', function() {
    if (resultadoActual && resultadoActual.pdf_url) {
      window.open(resultadoActual.pdf_url, '_blank');
    } else {
      alert('No se pudo generar el PDF.');
    }
  });

  enviarPdfBtn.addEventListener('click', function() {
    emailEnvio.style.display = 'block';
  });

  confirmarEnvioBtn.addEventListener('click', async function() {
    const email = document.getElementById('email-destino').value;
    if (!email) {
      alert('Ingresá un email válido.');
      return;
    }
    try {
      const res = await fetch('/api/enviar_pdf_paciente', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({dni: document.getElementById('dni-paciente').value, email})
      });
      const data = await res.json();
      if (data.ok) {
        alert('Correo enviado correctamente.');
        emailEnvio.style.display = 'none';
      } else {
        alert('No se pudo enviar el correo.');
      }
    } catch (err) {
      alert('Error al enviar el correo.');
    }
  });

  borrarBtn.addEventListener('click', async function() {
    if (!confirm('¿Estás seguro de que querés borrar COMPLETAMENTE este paciente? Se hará un backup automático antes de eliminarlo.')) {
      return;
    }
    const dni = document.getElementById('dni-paciente').value;
    borrarBtn.disabled = true;
    borrarBtn.textContent = 'Borrando...';
    try {
      const res = await fetch('/api/borrar_paciente', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({dni})
      });
      const data = await res.json();
      if (data.ok) {
        alert('Paciente borrado y backup realizado con éxito.');
        location.reload();
      } else {
        alert('No se pudo borrar el paciente. Contactar a soporte.');
        borrarBtn.disabled = false;
        borrarBtn.textContent = 'Borrar paciente';
      }
    } catch (err) {
      alert('Error al intentar borrar el paciente.');
      borrarBtn.disabled = false;
      borrarBtn.textContent = 'Borrar paciente';
    }
  });
});
