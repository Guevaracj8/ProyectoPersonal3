requireAuth();

if (getRol() !== "admin") {
  alert("Acceso restringido. Solo administradores.");
  window.location.href = "/dashboard";
}

let todosLosUsuarios = [];

async function cargarUsuarios() {
  try {
    todosLosUsuarios = await api.get("/usuarios") || [];
    renderTabla(todosLosUsuarios);
  } catch (e) {
    document.getElementById("tbodyUsuarios").innerHTML =
      `<tr><td colspan="7" class="empty-msg">Error: ${e.message}</td></tr>`;
  }
}

function renderTabla(usuarios) {
  const tbody = document.getElementById("tbodyUsuarios");

  if (!usuarios.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty-msg">No hay usuarios registrados.</td></tr>';
    return;
  }

  tbody.innerHTML = usuarios.map(u => `
    <tr>
      <td>${u.id}</td>
      <td>${u.nombre}</td>
      <td>${u.apellido}</td>
      <td>${u.email}</td>
      <td><span class="badge badge-admin">${u.rol}</span></td>
      <td>
        <span class="badge ${u.activo ? 'badge-ok' : 'badge-critico'}">
          ${u.activo ? "Activo" : "Inactivo"}
        </span>
      </td>
      <td style="display:flex;gap:.4rem">
        <button class="btn-secondary" style="padding:.3rem .6rem;font-size:.8rem"
                onclick="editarUsuario(${u.id})">Editar</button>
        <button class="btn-danger"
                onclick="desactivarUsuario(${u.id}, ${u.activo})">
          ${u.activo ? "Desactivar" : "Activar"}
        </button>
      </td>
    </tr>`).join("");
}

document.getElementById("buscador").addEventListener("input", filtrar);
document.getElementById("filtroRol").addEventListener("change", filtrar);

function filtrar() {
  const texto = document.getElementById("buscador").value.toLowerCase();
  const rol   = document.getElementById("filtroRol").value;

  const filtrado = todosLosUsuarios.filter(u => {
    const coincideTexto = `${u.nombre} ${u.apellido} ${u.email}`.toLowerCase().includes(texto);
    const coincideRol   = rol ? u.rol === rol : true;
    return coincideTexto && coincideRol;
  });
  renderTabla(filtrado);
}

function abrirModal(usuario = null) {
  document.getElementById("modalTitulo").textContent = usuario ? "Editar Usuario" : "Nuevo Usuario";
  document.getElementById("usuarioId").value         = usuario?.id || "";
  document.getElementById("uNombre").value           = usuario?.nombre || "";
  document.getElementById("uApellido").value         = usuario?.apellido || "";
  document.getElementById("uEmail").value            = usuario?.email || "";
  document.getElementById("uRol").value              = usuario?.rol || "vendedor";
  document.getElementById("uPassword").value         = "";
  document.getElementById("modalError").classList.add("hidden");

  const pwdGroup = document.getElementById("passwordGroup");
  pwdGroup.querySelector("label").textContent = usuario
    ? "Nueva contraseña (dejar vacío para no cambiar)"
    : "Contraseña";

  document.getElementById("modalUsuario").classList.remove("hidden");
}

function cerrarModal() {
  document.getElementById("modalUsuario").classList.add("hidden");
}

function editarUsuario(id) {
  const u = todosLosUsuarios.find(x => x.id === id);
  if (u) abrirModal(u);
}

document.getElementById("formUsuario").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errDiv = document.getElementById("modalError");
  errDiv.classList.add("hidden");

  const id       = document.getElementById("usuarioId").value;
  const password = document.getElementById("uPassword").value;

  const body = {
    nombre:   document.getElementById("uNombre").value.trim(),
    apellido: document.getElementById("uApellido").value.trim(),
    email:    document.getElementById("uEmail").value.trim(),
    rol:      document.getElementById("uRol").value,
    ...(password && { password }),
  };

  try {
    if (id) {
      await api.put(`/usuarios/${id}`, body);
    } else {
      await api.post("/usuarios", body);
    }
    cerrarModal();
    await cargarUsuarios();
  } catch (err) {
    errDiv.textContent = err.message;
    errDiv.classList.remove("hidden");
  }
});

async function desactivarUsuario(id, activo) {
  const accion = activo ? "desactivar" : "activar";
  if (!confirm(`¿Deseas ${accion} este usuario?`)) return;
  try {
    await api.put(`/usuarios/${id}`, { activo: !activo });
    await cargarUsuarios();
  } catch (err) {
    alert("Error: " + err.message);
  }
}

cargarUsuarios();
