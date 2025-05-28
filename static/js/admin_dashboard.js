// ╔════════════════════════════════════╗
// ║      admin_dashboard.js            ║
// ╚════════════════════════════════════╝

async function obtenerInstituciones() {
  const res = await fetch('/api/instituciones/listar');
  if (!res.ok) return [];
  const data = await res.json();
  return data.instituciones || [];
}

async function obtenerUsuarios() {
  const res = await fetch('/api/usuarios/listar');
  if (!res.ok) return [];
  const data = await res.json();
  return data.usuarios || [];
}

async function actualizarTablas() {
  const insts = await obtenerInstituciones();
  const usuarios = await obtenerUsuarios();
  mostrarInstituciones(insts);
  mostrarUsuarios(usuarios);
}

function crearBoton(texto, clase, onclick) {
  const btn = document.createElement('button');
  btn.textContent = texto;
  btn.className = `btn ${clase}`;
  btn.addEventListener('click', onclick);
  return btn;
}

function mostrarInstituciones(lista) {
  const tbody = document.querySelector('#tabla-instituciones tbody');
  tbody.innerHTML = '';
  lista.forEach(inst => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${inst.id}</td><td>${inst.nombre}</td><td>${inst.estado}</td><td>${inst.total_pacientes}</td><td>${inst.total_usuarios}</td>`;
    const acciones = document.createElement('td');
    const accion = inst.estado === 'activa' ? 'pausar' : 'activar';
    acciones.appendChild(crearBoton(accion.charAt(0).toUpperCase()+accion.slice(1), accion, () => cambiarEstadoInst(inst.id, accion)));
    acciones.appendChild(crearBoton('Eliminar', 'eliminar', () => eliminarInstitucion(inst.id)));
    const exportLink = document.createElement('a');
    exportLink.href = `/exportar-pacientes/${inst.id}`;
    exportLink.className = 'btn exportar';
    exportLink.textContent = 'Exportar';
    acciones.appendChild(exportLink);
    tr.appendChild(acciones);
    tbody.appendChild(tr);
  });
}

function mostrarUsuarios(lista) {
  const tbody = document.querySelector('#tabla-usuarios tbody');
  tbody.innerHTML = '';
  lista.forEach(u => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${u.usuario}</td><td>${u.nombres}</td><td>${u.apellido}</td><td>${u.rol}</td><td>${u.institucion}</td><td>${u.activo ? 'Activo' : 'Inactivo'}</td>`;
    const acciones = document.createElement('td');
    acciones.appendChild(crearBoton('Eliminar', 'eliminar', () => eliminarUsuario(u.usuario)));
    tr.appendChild(acciones);
    tbody.appendChild(tr);
  });
}

async function cambiarEstadoInst(id, accion) {
  showAlert('alerta', accion === 'pausar' ? 'Pausando…' : 'Activando…', false, 2000);
  await fetch(`/api/instituciones/${accion}`, {method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({id})});
  await actualizarTablas();
}

async function eliminarInstitucion(id) {
  if (!confirm('¿Eliminar institución?')) return;
  showAlert('borrado', 'Eliminando…', false, 2000);
  await fetch('/api/instituciones/eliminar', {method:'DELETE', headers:{'Content-Type':'application/json'}, body: JSON.stringify({id})});
  await actualizarTablas();
}

async function eliminarUsuario(usuario) {
  if (!confirm('¿Eliminar usuario?')) return;
  showAlert('borrado', 'Eliminando…', false, 2000);
  await fetch('/api/usuarios/eliminar', {method:'DELETE', headers:{'Content-Type':'application/json'}, body: JSON.stringify({usuario})});
  await actualizarTablas();
}

document.addEventListener('DOMContentLoaded', actualizarTablas);
