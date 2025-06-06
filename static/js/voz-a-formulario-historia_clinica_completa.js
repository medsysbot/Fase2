// ╔════════════════════════════════════╗
// ║      voz-a-formulario-historia-completa.js      ║
// ╚════════════════════════════════════╝
/*──────────────────────────────────────────────*/
/*   FUNCIÓN PRINCIPAL: Activar Reconocimiento   */
/*──────────────────────────────────────────────*/

function activarVoz() {
  try {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Este navegador no soporta reconocimiento de voz.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "es-ES";
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onresult = function (event) {
      const texto = event.results[0][0].transcript.trim();
      const campoActivo = document.activeElement;

      if (campoActivo && (campoActivo.tagName === "INPUT" || campoActivo.tagName === "TEXTAREA")) {
        campoActivo.value += (campoActivo.value ? " " : "") + texto;
      }
    };

    recognition.onerror = function (event) {
      console.error("Error en reconocimiento de voz:", event.error);
      alert("Ocurrió un error con el reconocimiento de voz.");
    };

    recognition.start();
  } catch (e) {
    console.error("No se pudo activar la voz:", e);
    alert("Error al activar el reconocimiento de voz.");
  }
}
