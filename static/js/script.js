// ╔════════════════════════════════════╗
// ║      script.js      ║
// ╚════════════════════════════════════╝
function guardarFormulario() {
    const contenido = document.getElementById("contenido-formulario");
    if (!contenido) {
        alert("No se encontró el contenido del formulario.");
        return;
    }

    const data = {
        html: contenido.innerHTML,
        nombre_paciente: document.getElementById("nombre")?.value || "Paciente",
        tipo_documento: "formulario", // Podés personalizar esto si querés
    };

    fetch("https://production-60b7e.up.railway.app/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then((res) => {
        if (!res.ok) throw new Error("Error al guardar");
        alert("Formulario guardado correctamente.");
    })
    .catch((err) => {
        alert("Error al guardar el formulario.");
        console.error(err);
    });
}

function imprimirFormulario() {
    window.print();
}

function eliminarFormulario() {
    if (confirm("¿Estás seguro de eliminar este formulario?")) {
        const contenido = document.getElementById("contenido-formulario");
        if (contenido) {
            contenido.innerHTML = "<p>Formulario eliminado.</p>";
        }
        alert("Formulario eliminado correctamente.");
    }
}
