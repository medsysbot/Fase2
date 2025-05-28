// ╔════════════════════════════════════╗
// ║      synaptica_tester.js          ║
// ╚════════════════════════════════════╝

function $(id) { return document.getElementById(id); }

function mostrar(msg) {
  $("mensaje").textContent = msg;
}

$("probar").addEventListener("click", () => {
  const url = $("url").value.trim();
  if (!url) {
    mostrar("Ingrese una URL válida.");
    return;
  }
  mostrar("Cargando…");
  const iframe = $("visor");
  iframe.src = url;

  iframe.onload = () => {
    try {
      const doc = iframe.contentDocument || iframe.contentWindow.document;
      if (!doc) throw new Error();
      const campos = doc.querySelectorAll("input, textarea");
      if (campos.length === 0) {
        mostrar("No se encontraron campos en el formulario.");
      } else {
        mostrar("Formulario cargado correctamente. Puede continuar.");
      }
    } catch (e) {
      mostrar(
        "No se pudo acceder por política de origen cruzado. Abra la URL en otra pestaña."
      );
    }
  };
});

fetch("/tester/estado")
  .then((r) => (r.ok ? r.json() : { activa: false }))
  .then((d) => {
    if (!d.activa) {
      mostrar("No hay una sesión activa. Inicie sesión para usar el tester.");
    }
  })
  .catch(() => {
    mostrar("No se pudo verificar la sesión actual.");
  });
