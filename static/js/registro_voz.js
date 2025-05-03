let campoActivo = null;

document.querySelectorAll("input").forEach((campo) => {
  campo.addEventListener("focus", () => {
    campoActivo = campo;
  });
});

function activarVoz() {
  if (!('webkitSpeechRecognition' in window)) {
    alert("Tu navegador no soporta reconocimiento de voz.");
    return;
  }

  const reconocimiento = new webkitSpeechRecognition();
  reconocimiento.lang = "es-ES";
  reconocimiento.interimResults = false;
  reconocimiento.maxAlternatives = 1;

  reconocimiento.onresult = function (evento) {
    const texto = evento.results[0][0].transcript;
    if (campoActivo) {
      campoActivo.value = texto;
    }
  };

  reconocimiento.onerror = function (evento) {
    console.error("Error de reconocimiento: ", evento.error);
  };

  reconocimiento.start();
}
