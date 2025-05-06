function showAlert(type, message, withButtons = false) {
  const iconos = {
    alerta: "/static/icons/alerta/alerta-alerta.png",
    borrado: "/static/icons/alerta/alerta-borrado.png",
    busqueda: "/static/icons/alerta/alerta-busqueda.png",
    error: "/static/icons/alerta/alerta-error.png",
    guardado: "/static/icons/alerta/alerta-guardado.png",
    suceso: "/static/icons/alerta/alerta-suceso.png",
    pacienteCargado: "/static/icons/alerta/alerta-paciente-cargado.png",
    pdf: "/static/icons/alerta/alerta-pdf.png"
  };

  const icono = document.getElementById("alert-icon");
  const texto = document.getElementById("alert-text");
  const botones = document.getElementById("alert-buttons");
  const contenedor = document.getElementById("alert-manager");

  icono.src = iconos[type] || iconos["alerta"];
  texto.textContent = message;
  botones.style.display = withButtons ? "flex" : "none";
  contenedor.style.display = "flex";

  if (!withButtons) {
    setTimeout(() => {
      contenedor.style.display = "none";
    }, 2500);
  }
}

function closeAlert() {
  document.getElementById("alert-manager").style.display = "none";
}

// Cierra el cartel cuando se hace clic en botón "no"
document.getElementById("btn-no").onclick = closeAlert;

// Confirma borrado y cierra cartel
document.getElementById("btn-borrar").onclick = function () {
  if (typeof confirmarBorradoPaciente === "function") {
    confirmarBorradoPaciente();
  }
  closeAlert();
};
