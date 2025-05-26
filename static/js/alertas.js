// ╔════════════════════════════════════╗
// ║      alertas.js      ║
// ╚════════════════════════════════════╝
let alertTimeout = null;

function showAlert(type, message, withButtons = false, duration = 3000) {
  const iconos = {
    alerta: "/static/icons/alerta/alerta-alerta.png",
    borrado: "/static/icons/alerta/alerta-borrado.png",
    busqueda: "/static/icons/alerta/alerta-busqueda.png",
    error: "/static/icons/alerta/alerta-error.png",
    guardado: "/static/icons/alerta/alerta-guardado.png",
    suceso: "/static/icons/alerta/alerta-suceso.png",
    pacienteCargado: "/static/icons/alerta/alerta-paciente-cargado.png",
    pdf: "/static/icons/alerta/alerta-pdf.png",
    email: "/static/icons/alerta/alerta-email.png",
    cargaPDF: "/static/icons/alerta/alerta-carga-pdf.png"
  };

  const icono = document.getElementById("alert-icon");
  const texto = document.getElementById("alert-text");
  const botones = document.getElementById("alert-buttons");
  const contenedor = document.getElementById("alert-manager");

  icono.src = iconos[type] || iconos["alerta"];
  texto.textContent = message;
  botones.style.display = withButtons ? "flex" : "none";
  contenedor.style.display = "flex";

  if (!withButtons && duration !== "infinito") {
    clearTimeout(alertTimeout);
    alertTimeout = setTimeout(() => {
      contenedor.style.display = "none";
    }, duration);
  }
}
