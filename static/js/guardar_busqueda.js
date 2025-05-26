// ╔════════════════════════════════════╗
// ║      guardar_busqueda.js      ║
// ╚════════════════════════════════════╝
document.addEventListener("DOMContentLoaded", function () {
  const botonGuardar = document.querySelector("button[title='Guardar']");

  if (botonGuardar) {
    botonGuardar.addEventListener("click", async function () {
      const busqueda = document.getElementById("busqueda")?.value;

      if (!busqueda) {
        alert("Por favor, ingrese un nombre o DNI antes de guardar.");
        return;
      }

      try {
        const formData = new FormData();
        formData.append('dni', busqueda);
        const response = await fetch("/buscar_paciente", {
          method: "POST",
          body: formData
        });

        if (response.ok) {
          alert("PDF generado correctamente.");
          document.querySelector(".visor-pdf iframe").src = "/static/doc/busqueda-generada.pdf?" + new Date().getTime();
        } else {
          alert("Error al generar el PDF.");
        }
      } catch (error) {
        console.error("Error:", error);
        alert("Error al conectar con el servidor.");
      }
    });
  }
});