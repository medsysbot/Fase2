// ╔════════════════════════════════════╗
// ║      guardar_busqueda.js      ║
// ╚════════════════════════════════════╝
document.addEventListener("DOMContentLoaded", function () {
  const botonGuardar = document.querySelector("button[title='Guardar']");
  const botonBuscar = document.querySelector("button[title='Buscar']");

  async function ejecutarBusqueda() {
    const dni = document.getElementById("busqueda")?.value.trim();

    if (!dni) {
      showAlert("error", "Por favor, ingrese un DNI válido.", false, 3000);
      return;
    }

    try {
      showAlert("guardado", "Buscando…", false, 3000);
      await new Promise(r => setTimeout(r, 3200));

      const formData = new FormData();
      formData.append('dni', dni);
      const response = await fetch("/buscar_paciente", {
        method: "POST",
        body: formData
      });
      const resultado = await response.json();

      if (response.ok && resultado.exito) {
        const datos = resultado.datos || {};
        document.getElementById('res-nombre').textContent = datos.nombres || '-';
        document.getElementById('res-apellido').textContent = datos.apellido || '-';
        document.getElementById('res-telefono').textContent = datos.telefono || '-';
        document.getElementById('res-email').textContent = datos.email || '-';
        showAlert("suceso", "Paciente encontrado", false, 3000);
      } else {
        showAlert("error", resultado.mensaje || "Paciente no encontrado", false, 4000);
      }
    } catch (error) {
      console.error("Error:", error);
      showAlert("error", "Error al conectar con el servidor", false, 4000);
    }
  }

  if (botonGuardar) {
    botonGuardar.addEventListener("click", ejecutarBusqueda);
  }
  if (botonBuscar) {
    botonBuscar.addEventListener("click", ejecutarBusqueda);
  }
});

function imprimirPagina() {
  window.print();
}
