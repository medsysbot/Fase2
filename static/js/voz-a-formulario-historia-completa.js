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
      "edad": "edad",
      "dni": "dni",
      "fecha de nacimiento": "fecha_nacimiento",
      "sexo": "sexo",
      "domicilio": "domicilio",
      "teléfono": "telefono",
      "correo": "email",
      "email": "email",
      "obra social": "obra_social",
      "prepaga": "obra_social",
      "afiliado": "nro_afiliado",
      "antecedentes personales": "antecedentes_personales",
      "antecedentes familiares": "antecedentes_familiares",
      "hábitos": "habitos",
      "crónicas": "cronicas",
      "internaciones": "cirugias",
      "cirugías": "cirugias",
      "medicación actual": "medicacion",
      "estudios": "estudios",
      "motivo de consulta": "motivo",
      "diagnóstico": "diagnostico",
      "tratamiento": "tratamiento",
      "instrucciones": "instrucciones",
      "próxima consulta": "proxima_consulta",
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

document.addEventListener("keydown", (e) => {
  if (e.code === "Space") {
    e.preventDefault();
    iniciarReconocimiento();
  }
});