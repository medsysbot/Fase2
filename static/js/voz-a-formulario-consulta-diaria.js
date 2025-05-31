// ╔════════════════════════════════════╗
// ║      voz-a-formulario-historia-evolucion.js      ║
// ╚════════════════════════════════════╝
function iniciarReconocimiento() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'es-AR';
  recognition.interimResults = false;
  recognition.continuous = false;

  recognition.onresult = (event) => {
    const texto = event.results[0][0].transcript.toLowerCase();
    console.log("Texto dictado:", texto);

    const campos = {
      "paciente": "paciente",
      "fecha de evolución": "fecha",
      "diagnóstico del día": "diagnostico",
      "evolución clínica": "evolucion",
      "indicaciones médicas": "indicaciones",
      "profesional": "profesional"
    };

    for (const clave in campos) {
      if (texto.includes(clave)) {
        const idCampo = campos[clave];
        const valor = texto.replace(clave, "").trim();
        const campo = document.getElementById(idCampo);
        if (campo) campo.value = valor;
        break;
      }
    }
  };

  recognition.onerror = (e) => console.error("Error de voz:", e.error);
  recognition.start();
}
