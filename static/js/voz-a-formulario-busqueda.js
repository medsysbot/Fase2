// ╔════════════════════════════════════╗
// ║      voz-a-formulario-busqueda.js      ║
// ╚════════════════════════════════════╝
function iniciarReconocimiento() {
  const campo = document.getElementById("busqueda");
  if (!campo) return;

  const reconocimiento = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  reconocimiento.lang = "es-ES";

  reconocimiento.onresult = function (event) {
    const resultado = event.results[0][0].transcript;
    campo.value = resultado;
  };

  reconocimiento.onerror = function (event) {
    console.error("Error de reconocimiento de voz:", event.error);
    alert("Hubo un problema con el reconocimiento de voz.");
  };

  reconocimiento.start();
}