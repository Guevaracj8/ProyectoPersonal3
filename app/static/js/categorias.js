requireAuth();

let todasLasCategorias = [];

async function cargarCategorias() {
  try {
    todasLasCategorias = await api.get("/categorias") || [];
    renderTabla(todasLasCategorias);
  } catch (e) {
    document.getElementById("tbodyCategorias").innerHTML =
      `<tr><td colspan="4" class="empty-msg">Error: ${e.message}</td></tr>`;
  }
}

function renderTabla(categorias) {
  const tbody   = document.getElementById("tbodyCategorias");
  const esAdmin = getRol() === "admin";

  if (!categorias.length) {
    tbody.innerHTML = '<tr><td colspan="4" class="empty-msg">No hay categorías registradas.</td></tr>';
    return;
  }

  tbody.innerHTML = categorias.map(c => `
    <tr>
      <td>${c.id}</td>
      <td><strong>${c.nombre}</strong></td>
      <td>${c.descripcion || "—"}</td>
      <td style="display:flex;gap:.4rem">
        ${esAdmin ? `
          <button class="btn-secondary" style="padding:.3rem .6rem;font-size:.8rem"
                  onclick="editarCategoria(${c.id})">Editar</button>
          <button class="btn-danger"
                  onclick="eliminarCategoria(${c.id})">Eliminar</button>
        ` : "—"}
      </td>
    </tr>`).join("");
}

document.getElementById("buscador").addEventListener("input", () => {
  const texto    = document.getElementById("buscador").value.toLowerCase();
  const filtrado = todasLasCategorias.filter(c =>
    c.nombre.toLowerCase().includes(texto) ||
    (c.descripcion || "").toLowerCase().includes(texto)
  );
  renderTabla(filtrado);
});

function abrirModal(categoria = null) {
  document.getElementById("modalTitulo").textContent = categoria ? "Editar Categoría" : "Nueva Categoría";
  document.getElementById("categoriaId").value       = categoria?.id || "";
  document.getElementById("cNombre").value           = categoria?.nombre || "";
  document.getElementById("cDescripcion").value      = categoria?.descripcion || "";
  document.getElementById("modalError").classList.add("hidden");
  document.getElementById("modalCategoria").classList.remove("hidden");
}

function cerrarModal() {
  document.getElementById("modalCategoria").classList.add("hidden");
}

function editarCategoria(id) {
  const c = todasLasCategorias.find(x => x.id === id);
  if (c) abrirModal(c);
}

document.getElementById("formCategoria").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errDiv = document.getElementById("modalError");
  errDiv.classList.add("hidden");

  const id   = document.getElementById("categoriaId").value;
  const body = {
    nombre:      document.getElementById("cNombre").value.trim(),
    descripcion: document.getElementById("cDescripcion").value.trim() || null,
  };

  try {
    if (id) {
      await api.put(`/categorias/${id}`, body);
    } else {
      await api.post("/categorias", body);
    }
    cerrarModal();
    await cargarCategorias();
  } catch (err) {
    errDiv.textContent = err.message;
    errDiv.classList.remove("hidden");
  }
});

async function eliminarCategoria(id) {
  if (!confirm("¿Eliminar esta categoría?")) return;
  try {
    await api.delete(`/categorias/${id}`);
    await cargarCategorias();
  } catch (err) {
    alert("Error: " + err.message);
  }
}

cargarCategorias();
