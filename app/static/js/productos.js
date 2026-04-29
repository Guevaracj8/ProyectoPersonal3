requireAuth();

let todosLosProductos = [];
let categorias        = [];

async function init() {
  if (getRol() === "admin") {
    document.getElementById("adminActions").classList.remove("hidden");
  }
  await Promise.all([cargarCategorias(), cargarProductos()]);
}

async function cargarCategorias() {
  try {
    categorias = await api.get("/categorias") || [];
    const sel  = document.getElementById("pCategoria");
    sel.innerHTML = categorias.map(c => `<option value="${c.id}">${c.nombre}</option>`).join("");
  } catch (e) {
    console.error("Error cargando categorías:", e.message);
  }
}

async function cargarProductos() {
  try {
    todosLosProductos = await api.get("/productos") || [];
    renderTabla(todosLosProductos);
  } catch (e) {
    document.getElementById("tbodyProductos").innerHTML =
      `<tr><td colspan="9" class="empty-msg">Error: ${e.message}</td></tr>`;
  }
}

function renderTabla(productos) {
  const tbody = document.getElementById("tbodyProductos");
  if (!productos.length) {
    tbody.innerHTML = '<tr><td colspan="9" class="empty-msg">No hay productos registrados.</td></tr>';
    return;
  }

  const esAdmin = getRol() === "admin";
  tbody.innerHTML = productos.map(p => {
    const cat    = categorias.find(c => c.id === p.categoria_id);
    const estado = p.en_stock_critico
      ? '<span class="badge badge-critico">CRÍTICO</span>'
      : '<span class="badge badge-ok">OK</span>';
    const acciones = esAdmin
      ? `<button class="btn-secondary" style="padding:.3rem .6rem;font-size:.8rem" onclick="editarProducto(${p.id})">Editar</button>
         <button class="btn-danger" onclick="eliminarProducto(${p.id})">Eliminar</button>`
      : "—";

    return `<tr>
      <td>${p.id}</td>
      <td>${p.nombre}</td>
      <td>${cat ? cat.nombre : p.categoria_id}</td>
      <td>$ ${p.precio_compra.toFixed(2)}</td>
      <td>$ ${p.precio_venta.toFixed(2)}</td>
      <td>${p.stock_actual}</td>
      <td>${p.stock_minimo}</td>
      <td>${estado}</td>
      <td style="display:flex;gap:.4rem">${acciones}</td>
    </tr>`;
  }).join("");
}

document.getElementById("buscador").addEventListener("input", filtrar);
document.getElementById("filtroStock").addEventListener("change", filtrar);

function filtrar() {
  const texto   = document.getElementById("buscador").value.toLowerCase();
  const soloSC  = document.getElementById("filtroStock").value === "critico";
  const filtrado = todosLosProductos.filter(p => {
    const coincide = p.nombre.toLowerCase().includes(texto);
    return soloSC ? coincide && p.en_stock_critico : coincide;
  });
  renderTabla(filtrado);
}

function abrirModalProducto(producto = null) {
  document.getElementById("modalTitulo").textContent = producto ? "Editar Producto" : "Nuevo Producto";
  document.getElementById("productoId").value        = producto?.id || "";
  document.getElementById("pNombre").value           = producto?.nombre || "";
  document.getElementById("pDescripcion").value      = producto?.descripcion || "";
  document.getElementById("pCategoria").value        = producto?.categoria_id || "";
  document.getElementById("pCompra").value           = producto?.precio_compra || "";
  document.getElementById("pVenta").value            = producto?.precio_venta || "";
  document.getElementById("pStock").value            = producto?.stock_actual ?? "";
  document.getElementById("pMinimo").value           = producto?.stock_minimo ?? 5;
  document.getElementById("modalError").classList.add("hidden");

  document.getElementById("pStock").disabled = !!producto;

  document.getElementById("modalProducto").classList.remove("hidden");
}

function cerrarModal() {
  document.getElementById("modalProducto").classList.add("hidden");
}

async function editarProducto(id) {
  const p = todosLosProductos.find(x => x.id === id);
  if (p) abrirModalProducto(p);
}

document.getElementById("formProducto").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errDiv = document.getElementById("modalError");
  errDiv.classList.add("hidden");

  const id = document.getElementById("productoId").value;

  const body = {
    nombre:        document.getElementById("pNombre").value,
    descripcion:   document.getElementById("pDescripcion").value || null,
    categoria_id:  parseInt(document.getElementById("pCategoria").value),
    precio_compra: parseFloat(document.getElementById("pCompra").value),
    precio_venta:  parseFloat(document.getElementById("pVenta").value),
    stock_minimo:  parseInt(document.getElementById("pMinimo").value),
    ...(!id && { stock_actual: parseInt(document.getElementById("pStock").value) }),
  };

  try {
    if (id) {
      await api.put(`/productos/${id}`, body);
    } else {
      await api.post("/productos", body);
    }
    cerrarModal();
    await cargarProductos();
  } catch (err) {
    errDiv.textContent = err.message;
    errDiv.classList.remove("hidden");
  }
});

async function eliminarProducto(id) {
  if (!confirm("¿Eliminar este producto? Esta acción no se puede deshacer.")) return;
  try {
    await api.delete(`/productos/${id}`);
    await cargarProductos();
  } catch (err) {
    alert("Error: " + err.message);
  }
}

init();
