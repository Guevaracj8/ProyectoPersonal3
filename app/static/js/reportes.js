requireAuth();

if (getRol() !== "admin") {
  alert("Acceso restringido. Solo administradores.");
  window.location.href = "/dashboard";
}

function descargarArchivo(url, nombre) {
  const token = getToken();
  fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    .then(res => {
      if (!res.ok) throw new Error("Error al generar el archivo.");
      return res.blob();
    })
    .then(blob => {
      const link  = document.createElement("a");
      link.href   = URL.createObjectURL(blob);
      link.download = nombre;
      link.click();
      URL.revokeObjectURL(link.href);
    })
    .catch(err => alert("Error: " + err.message));
}

function descargarPDFVentas() {
  const periodo = document.getElementById("periodoPDF").value;
  descargarArchivo(`/reportes/pdf/ventas?periodo=${periodo}`, `reporte_${periodo}.pdf`);
}

function descargarRecibo() {
  const id     = document.getElementById("ventaIdRecibo").value;
  const errDiv = document.getElementById("reciboError");
  errDiv.classList.add("hidden");

  if (!id) {
    errDiv.textContent = "Ingresa un ID de venta válido.";
    errDiv.classList.remove("hidden");
    return;
  }
  descargarArchivo(`/reportes/pdf/recibo/${id}`, `recibo_venta_${id}.pdf`);
}

function descargarExcelVentas() {
  const desde = document.getElementById("excelDesde").value;
  const hasta = document.getElementById("excelHasta").value;
  const params = [];
  if (desde) params.push(`fecha_inicio=${desde}T00:00:00`);
  if (hasta) params.push(`fecha_fin=${hasta}T23:59:59`);
  const qs = params.length ? "?" + params.join("&") : "";
  descargarArchivo(`/reportes/excel/ventas${qs}`, "ventas.xlsx");
}

function descargarExcelInventario() {
  descargarArchivo("/reportes/excel/inventario", "inventario.xlsx");
}
