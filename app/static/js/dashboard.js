requireAuth();

async function cargarDashboard() {
  try {
    const productos = await api.get("/productos");
    if (productos) {
      document.getElementById("totalProductos").textContent = productos.length;
      const criticos = productos.filter(p => p.en_stock_critico);
      document.getElementById("totalCritico").textContent   = criticos.length;

      const lista = document.getElementById("stockCriticoList");
      if (criticos.length === 0) {
        lista.innerHTML = '<p class="empty-msg">No hay productos en stock crítico.</p>';
      } else {
        lista.innerHTML = `
          <table>
            <thead><tr>
              <th>ID</th><th>Producto</th>
              <th>Stock Actual</th><th>Stock Mínimo</th><th>Estado</th>
            </tr></thead>
            <tbody>
              ${criticos.map(p => `
                <tr>
                  <td>${p.id}</td>
                  <td>${p.nombre}</td>
                  <td>${p.stock_actual}</td>
                  <td>${p.stock_minimo}</td>
                  <td><span class="badge badge-critico">⚠ CRÍTICO</span></td>
                </tr>`).join("")}
            </tbody>
          </table>`;
      }
    }

    if (getRol() === "admin") {
      const resumen = await api.get("/ventas/resumen?periodo=semanal");
      if (resumen) {
        document.getElementById("ventasSemana").textContent    = resumen.total_ventas;
        document.getElementById("gananciasSemana").textContent = `$ ${resumen.ganancias_totales.toLocaleString("es-VE", { minimumFractionDigits: 2 })}`;
      }
    } else {
      document.getElementById("ventasSemana").textContent    = "—";
      document.getElementById("gananciasSemana").textContent = "—";
    }

  } catch (err) {
    console.error("Error cargando dashboard:", err.message);
  }
}

cargarDashboard();
