function showAlert(type, message, withButtons = false) {
  const iconos = {
    alerta: "static/icons/alerta/alerta-alerta.png",
    borrado: "static/icons/alerta/alerta-borrado.png",
    busqueda: "static/icons/alerta/alerta-busqueda.png",
    error: "static/icons/alerta/alerta-error.png",
    guardado: "static/icons/alerta/alerta-guardado.png",
    suceso: "static/icons/alerta/alerta-suceso.png",
    pacienteCargado: "static/icons/alerta/alerta-paciente-cargado.png"
  };

  document.getElementById("alert-icon").src = iconos[type] || iconos["alerta"];
  document.getElementById("alert-text").textContent = message;
  document.getElementById("alert-buttons").style.display = withButtons ? "flex" : "none";
  document.getElementById("alert-manager").style.display = "flex";
}

function closeAlert() {
  document.getElementById("alert-manager").style.display = "none";
}

document.getElementById("btn-no").onclick = closeAlert;

document.getElementById("btn-borrar").onclick = function () {
  console.log("Acción confirmada");
  closeAlert();
};
