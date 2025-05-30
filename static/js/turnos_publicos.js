window.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    document.getElementById('splash').style.display = 'none';
    document.getElementById('turnos-form').style.display = 'block';
    document.body.style.overflow = 'auto';
  }, 1800);

  cargarEspecialidades();

  document.getElementById('especialidad').addEventListener('change', (e) => {
    cargarProfesionales(e.target.value);
  });

  document.getElementById('fecha').addEventListener('change', () => {
    const prof = document.getElementById('profesional').value;
    const fecha = document.getElementById('fecha').value;
    if (prof && fecha) {
      cargarHorarios(prof, fecha);
    }
  });

  document.getElementById('form-turno').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const res = await fetch('/solicitar_turno', { method: 'POST', body: formData });
    const data = await res.json();
    const alerta = document.getElementById('alerta-turno');
    if (data.exito) {
      alerta.style.color = '#16a085';
      alerta.textContent = 'Turno registrado. Revisá tu e-mail.';
    } else {
      alerta.style.color = '#e74c3c';
      alerta.textContent = data.mensaje || 'Error al solicitar turno';
    }
    alerta.style.display = 'block';
  });
});

async function cargarEspecialidades() {
  const res = await fetch('/api/especialidades');
  const data = await res.json();
  const select = document.getElementById('especialidad');
  select.innerHTML = '<option value="">Especialidad</option>';
  data.forEach((item) => {
    const opt = document.createElement('option');
    opt.value = item;
    opt.textContent = item;
    select.appendChild(opt);
  });
}

async function cargarProfesionales(especialidad) {
  const res = await fetch(`/api/profesionales?especialidad=${encodeURIComponent(especialidad)}`);
  const data = await res.json();
  const select = document.getElementById('profesional');
  select.innerHTML = '<option value="">Profesional</option>';
  data.forEach((item) => {
    const opt = document.createElement('option');
    opt.value = item;
    opt.textContent = item;
    select.appendChild(opt);
  });
  document.getElementById('horario').innerHTML = '<option value="">Horario</option>';
}

async function cargarHorarios(profesional, fecha) {
  const res = await fetch(`/api/horarios?profesional=${encodeURIComponent(profesional)}&fecha=${fecha}`);
  const data = await res.json();
  const select = document.getElementById('horario');
  select.innerHTML = '<option value="">Horario</option>';
  data.forEach((h) => {
    const opt = document.createElement('option');
    opt.value = h;
    opt.textContent = h;
    select.appendChild(opt);
  });
}
