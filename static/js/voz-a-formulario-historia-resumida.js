// ╔════════════════════════════════════╗
// ║      voz-a-formulario-historia-resumida.js      ║
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
      "fecha de nacimiento": "fecha_nacimiento",
      "edad": "edad",
      "sexo": "sexo",
      "obra social": "obra_social",
      "prepaga": "obra_social",
      "afiliado": "nro_afiliado",
      "contacto de emergencia": "contacto_emergencia",
      "diagnóstico": "diagnostico",
      "diagnóstico de la consulta": "diagnostico",
      "diagnósticos médicos relevantes": "diagnosticos",
      "alergias": "alergias",
      "medicación habitual": "medicacion",
      "cirugías": "cirugias",
      "estudios complementarios": "estudios",
      "motivo de la consulta": "motivo",
      "tratamiento indicado": "tratamiento",
      "instrucciones": "instrucciones",
      "próxima consulta": "proxima_consulta",
      "información relevante": "info_relevante",
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

// El reconocimiento se activa únicamente desde el botón de micrófono.
