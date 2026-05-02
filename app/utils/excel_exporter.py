import pandas as pd
import io


def exportar_ventas_excel(ventas: list) -> bytes:
    filas = []
    for v in ventas:
        for d in v.detalles:
            filas.append({
                "Venta ID":       v.id,
                "Fecha":          v.fecha.strftime("%d/%m/%Y %H:%M") if v.fecha else "",
                "Vendedor ID":    v.usuario_id,
                "Estado":         v.estado,
                "Producto ID":    d.producto_id,
                "Cantidad":       d.cantidad,
                "Precio Unitario":d.precio_unitario,
                "Subtotal":       d.subtotal,
                "Ganancia Línea": d.ganancia_linea,
                "Total Venta":    v.total_calculado,
                "Ganancia Total": v.ganancia_calculada,
            })

    df = pd.DataFrame(filas) if filas else pd.DataFrame(columns=[
        "Venta ID", "Fecha", "Vendedor ID", "Estado",
        "Producto ID", "Cantidad", "Precio Unitario", "Subtotal",
        "Ganancia Línea", "Total Venta", "Ganancia Total",
    ])

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Ventas")
        ws = writer.sheets["Ventas"]
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col) + 4
            ws.column_dimensions[col[0].column_letter].width = min(max_len, 30)

    buffer.seek(0)
    return buffer.read()


def exportar_inventario_excel(productos: list) -> bytes:
    filas = [
        {
            "ID":                   p.id,
            "Nombre":               p.nombre,
            "Descripción":          p.descripcion or "",
            "Categoría ID":         p.categoria_id,
            "Precio Compra ($)":    p.precio_compra,
            "Precio Venta ($)":     p.precio_venta,
            "Margen ($)":           round(p.precio_venta - p.precio_compra, 2),
            "Stock Actual":         p.stock_actual,
            "Stock Mínimo":         p.stock_minimo,
            "Estado Stock":         "⚠ CRÍTICO" if p.stock_actual <= p.stock_minimo else "OK",
            "Última Actualización": p.fecha_actualizacion.strftime("%d/%m/%Y") if p.fecha_actualizacion else "",
        }
        for p in productos
    ]

    df = pd.DataFrame(filas) if filas else pd.DataFrame()

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Inventario")
        ws = writer.sheets["Inventario"]
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col) + 4
            ws.column_dimensions[col[0].column_letter].width = min(max_len, 35)

    buffer.seek(0)
    return buffer.read()
