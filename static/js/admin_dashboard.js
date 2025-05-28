// ╔════════════════════════════════════╗
// ║      admin_dashboard.js            ║
// ╚════════════════════════════════════╝

async function obtenerUsuarios() {
  const res = await fetch('/api/usuarios/institucion');
  if (!res.ok) return [];
  const data = await res.json();
  return data.usuarios || [];
}

async function obtenerPacientes() {
  const res = await fetch('/api/pacientes/institucion');
  if (!res.ok) return [];
  const data = await res.json();
  return data.pacientes || [];
}

async function actualizarTablas() {
  const usuarios = await obtenerUsuarios();
  const pacientes = await obtenerPacientes();
  mostrarUsuarios(usuarios);
  mostrarPacientes(pacientes);
}

function crearBoton(texto, clase, onclick) {
  const btn = document.createElement('button');
  btn.textContent = texto;
  btn.className = `btn ${clase}`;
  btn.addEventListener('click', onclick);
  return btn;
}

function mostrarUsuarios(lista) {
  const tbody = document.querySelector('#tabla-usuarios tbody');
  tbody.innerHTML = '';
  lista.forEach(u => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${u.usuario}</td><td>${u.nombres}</td><td>${u.apellido}</td><td>${u.rol}</td><td>${u.institucion}</td><td>${u.activo ? 'Activo' : 'Inactivo'}</td>`;
    const acciones = document.createElement('td');
    if (u.activo) {
      acciones.appendChild(crearBoton('Suspender', 'eliminar', () => cambiarEstadoUsuario(u.usuario, false)));
    } else {
      acciones.appendChild(crearBoton('Reactivar', 'exportar', () => cambiarEstadoUsuario(u.usuario, true)));
    }
    acciones.appendChild(crearBoton('Eliminar', 'eliminar', () => eliminarUsuario(u.usuario)));
    tr.appendChild(acciones);
    tbody.appendChild(tr);
  });
}

function mostrarPacientes(lista) {
  const tbody = document.querySelector('#tabla-pacientes tbody');
  tbody.innerHTML = '';
  lista.forEach(p => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${p.dni}</td><td>${p.nombres}</td><td>${p.apellido}</td>`;
    const acciones = document.createElement('td');
    acciones.appendChild(crearBoton('Descargar', 'exportar', () => descargarPaciente(p.dni)));
    acciones.appendChild(crearBoton('Eliminar', 'eliminar', () => eliminarPaciente(p.dni)));
    tr.appendChild(acciones);
    tbody.appendChild(tr);
  });
}

async function descargarPaciente(dni) {
  showAlert('cargaPDF', 'Preparando descarga…', false, 2000);
  const res = await fetch(`/api/pacientes/descargar/${dni}`);
  if (res.ok) {
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `paciente_${dni}.zip`;
    a.click();
    window.URL.revokeObjectURL(url);
  } else {
    showAlert('error', 'No se pudo descargar', false, 3000);
  }
}

async function eliminarPaciente(dni) {
  if (!confirm('¿Eliminar paciente?')) return;
  showAlert('borrado', 'Eliminando…', false, 2000);
  await fetch('/eliminar_paciente', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({dni})
  });
  await actualizarTablas();
}

async function eliminarUsuario(usuario) {
  if (!confirm('¿Eliminar usuario?')) return;
  showAlert('borrado', 'Eliminando…', false, 2000);
  await fetch('/api/usuarios/eliminar', {method:'DELETE', headers:{'Content-Type':'application/json'}, body: JSON.stringify({usuario})});
  await actualizarTablas();
}

async function cambiarEstadoUsuario(usuario, activo) {
  await fetch('/api/usuarios/estado', {method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify({usuario, activo})});
  await actualizarTablas();
}

async function agregarUsuario() {
  const form = document.getElementById('form-nuevo-usuario');
  const datos = {
    usuario: form.querySelector('#usuario').value.trim(),
    contrasena: form.querySelector('#contrasena').value.trim(),
    nombres: form.querySelector('#nombres').value.trim(),
    apellido: form.querySelector('#apellido').value.trim(),
    rol: form.querySelector('#rol').value,
    institucion: parseInt(form.querySelector('#institucion').value, 10)
  };
  await fetch('/api/usuarios/agregar', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(datos)});
  form.reset();
  await actualizarTablas();
}

document.addEventListener('DOMContentLoaded', actualizarTablas);
document.getElementById('btn-agregar-usuario').addEventListener('click', agregarUsuario);
