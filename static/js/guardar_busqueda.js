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
        const response = await fetch("/guardar_busqueda", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ busqueda: busqueda })
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