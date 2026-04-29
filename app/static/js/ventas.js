requireAuth();

let productosDisponibles = [];
let itemCount = 0;

async function init() {
  productosDisponibles = await api.get("/productos") || [];
  agregarItem();      
  await cargarVentas();
}

function agregarItem() {
  itemCount++;
  const div  = document.createElement("div");
  div.id     = `item-${itemCount}`;
  div.style  = "display:grid;grid-template-columns:2fr 1fr auto;gap:.8rem;align-items:end;margin-bottom:.8rem";

  div.innerHTML = `
    <div class="form-group" style="margin:0">
      <label>Producto</label>
      <select id="prod-${itemCount}" onchange="actualizarResumen()">
        <option value="">-- Seleccionar --</option>
        ${productosDisponibles.map(p =>
          `<option value="${p.id}" data-venta="${p.precio_venta}" data-stock="${p.stock_actual}">
            ${p.nombre} (Stock: ${p.stock_actual})
          </option>`
        ).join("")}
      </select>
    </div>
    <div class="form-group" style="margin:0">
      <label>Cantidad</label>
      <input type="number" id="qty-${itemCount}" min="1" value="1" onchange="actualizarResumen()"
             style="padding:.65rem .9rem;border:1.5px solid var(--border);border-radius:8px;width:100%"/>
    </div>
    <button onclick="quitarItem(${itemCount})" class="btn-danger" style="margin-bottom:0;height:42px">✕</button>
  `;
  document.getElementById("itemsVenta").appendChild(div);
}

function quitarItem(id) {
  const el = document.getElementById(`item-${id}`);
  if (el) el.remove();
  actualizarResumen();
}

function actualizarResumen() {
  let total = 0;
  document.querySelectorAll("[id^='prod-']").forEach(sel => {
    const n   = sel.id.split("-")[1];
    const opt = sel.selectedOptions[0];
    if (!opt || !opt.value) return;
    const qty   = parseInt(document.getElementById(`qty-${n}`)?.value) || 0;
    const price = parseFloat(opt.dataset.venta) || 0;
    total += price * qty;
  });
  document.getElementById("resumenVenta").classList.remove("hidden");
  document.getElementById("totalEstimado").textContent =
    `$ ${total.toLocaleString("es-VE", { minimumFractionDigits: 2 })}`;
}

async function registrarVenta() {
  const errDiv  = document.getElementById("ventaError");
  const sucDiv  = document.getElementById("ventaSuccess");
  errDiv.classList.add("hidden");
  sucDiv.classList.add("hidden");
  document.getElementById("stockCriticoAlerta").classList.add("hidden");

  const items = [];
  document.querySelectorAll("[id^='prod-']").forEach(sel => {
    const n   = sel.id.split("-")[1];
    const pid = parseInt(sel.value);
    const qty = parseInt(document.getElementById(`qty-${n}`)?.value) || 0;
    if (pid && qty > 0) items.push({ producto_id: pid, cantidad: qty });
  });

  if (!items.length) {
    errDiv.textContent = "Agrega al menos un producto con cantidad válida.";
    errDiv.classList.remove("hidden");
    return;
  }

  try {
    const result = await api.post("/ventas", { items });

    if (result.stock_critico?.length) {
      document.getElementById("productosCriticos").textContent = result.stock_critico.join(", ");
      document.getElementById("stockCriticoAlerta").classList.remove("hidden");
    }

    sucDiv.textContent = `Venta #${result.id} registrada. Total: $ ${result.total_calculado.toFixed(2)} | Ganancia: $ ${result.ganancia_calculada.toFixed(2)}`;
    sucDiv.classList.remove("hidden");

    document.getElementById("itemsVenta").innerHTML = "";
    itemCount = 0;
    productosDisponibles = await api.get("/productos") || [];
    agregarItem();
    actualizarResumen();
    await cargarVentas();

  } catch (err) {
    errDiv.textContent = err.message;
    errDiv.classList.remove("hidden");
  }
}

async function cargarVentas() {
  const desde  = document.getElementById("fechaDesde")?.value;
  const hasta  = document.getElementById("fechaHasta")?.value;
  let url      = "/ventas";
  const params = [];
  if (desde) params.push(`fecha_inicio=${desde}T00:00:00`);
  if (hasta) params.push(`fecha_fin=${hasta}T23:59:59`);
  if (params.length) url += "?" + params.join("&");

  try {
    const ventas = await api.get(url) || [];
    const tbody  = document.getElementById("tbodyVentas");

    if (!ventas.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty-msg">No hay ventas en este período.</td></tr>';
      return;
    }

    tbody.innerHTML = ventas.map(v => `
      <tr>
        <td>${v.id}</td>
        <td>${v.fecha ? new Date(v.fecha).toLocaleString("es-VE") : "—"}</td>
        <td>${v.usuario_id}</td>
        <td>$ ${v.total_calculado.toFixed(2)}</td>
        <td>$ ${v.ganancia_calculada.toFixed(2)}</td>
        <td><span class="badge ${v.estado === 'pagado' ? 'badge-ok' : 'badge-critico'}">${v.estado}</span></td>
      </tr>`).join("");
  } catch (e) {
    console.error(e.message);
  }
}

init();
