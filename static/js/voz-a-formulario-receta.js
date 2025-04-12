let recognition;

function iniciarReconocimiento() {
  if (!('webkitSpeechRecognition' in window)) {
    alert("Tu navegador no soporta reconocimiento por voz");
    return;
  }

  recognition = new webkitSpeechRecognition();
  recognition.lang = "es-ES";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onresult = function(event) {
    const texto = event.results[0][0].transcript;
    insertarTexto(texto);
  };

  recognition.onerror = function(event) {
    console.error("Error en reconocimiento de voz:", event.error);
  };

  recognition.start();
}

function insertarTexto(texto) {
  const campos = document.querySelectorAll("input, textarea");
  for (let campo of campos) {
    if (campo === document.activeElement) {
      campo.value += (campo.value ? " " : "") + texto;
      campo.focus();
      break;
    }
  }
}
