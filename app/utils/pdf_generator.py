from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import io


def _doc(buffer):
    return SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )


def _estilos():
    styles = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "Titulo",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#1F4E79"),
        spaceAfter=6,
    )
    subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.gray,
        spaceAfter=12,
    )
    return styles, titulo, subtitulo


HEADER_COLOR = colors.HexColor("#1F4E79")
ROW_ALT      = colors.HexColor("#EAF3FB")


def generar_reporte_pdf(ventas, periodo: str, desde: datetime, hasta: datetime) -> bytes:
    buffer = io.BytesIO()
    doc    = _doc(buffer)
    styles, titulo, subtitulo = _estilos()

    total_ingresos  = sum(v.total_calculado for v in ventas)
    total_ganancias = sum(v.ganancia_calculada for v in ventas)

    elementos = [
        Paragraph("FerreStock — Reporte de Ventas", titulo),
        Paragraph(
            f"Período: {periodo.capitalize()} | Desde: {desde.strftime('%d/%m/%Y')} "
            f"hasta {hasta.strftime('%d/%m/%Y')}",
            subtitulo,
        ),
        Spacer(1, 0.4 * cm),
    ]

    resumen_data = [
        ["Métrica", "Valor"],
        ["Total de ventas",       str(len(ventas))],
        ["Ingresos totales",      f"$ {total_ingresos:,.2f}"],
        ["Ganancias netas",       f"$ {total_ganancias:,.2f}"],
        ["Generado el",           datetime.utcnow().strftime("%d/%m/%Y %H:%M")],
    ]
    tabla_resumen = Table(resumen_data, colWidths=[9 * cm, 8 * cm])
    tabla_resumen.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), HEADER_COLOR),
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("PADDING",      (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabla_resumen)
    elementos.append(Spacer(1, 0.6 * cm))

    if ventas:
        elementos.append(Paragraph("Detalle de Ventas", styles["Heading2"]))
        elementos.append(Spacer(1, 0.2 * cm))

        detalle_data = [["ID", "Fecha", "Vendedor ID", "Total", "Ganancia", "Estado"]]
        for v in ventas:
            detalle_data.append([
                str(v.id),
                v.fecha.strftime("%d/%m/%Y %H:%M") if v.fecha else "—",
                str(v.usuario_id),
                f"$ {v.total_calculado:,.2f}",
                f"$ {v.ganancia_calculada:,.2f}",
                v.estado,
            ])

        tabla_detalle = Table(detalle_data, colWidths=[1.5*cm, 4*cm, 3*cm, 3*cm, 3*cm, 2.5*cm])
        tabla_detalle.setStyle(TableStyle([
            ("BACKGROUND",     (0, 0), (-1, 0), HEADER_COLOR),
            ("TEXTCOLOR",      (0, 0), (-1, 0), colors.white),
            ("FONTNAME",       (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",       (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
            ("GRID",           (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ("PADDING",        (0, 0), (-1, -1), 5),
        ]))
        elementos.append(tabla_detalle)

    doc.build(elementos)
    buffer.seek(0)
    return buffer.read()


def generar_recibo_pdf(venta) -> bytes:
    buffer = io.BytesIO()
    doc    = _doc(buffer)
    styles, titulo, subtitulo = _estilos()

    elementos = [
        Paragraph("FerreStock — Recibo de Venta", titulo),
        Paragraph(
            f"Venta #{venta.id} | Fecha: {venta.fecha.strftime('%d/%m/%Y %H:%M') if venta.fecha else '—'} "
            f"| Estado: {venta.estado}",
            subtitulo,
        ),
        Spacer(1, 0.4 * cm),
    ]

    items_data = [["Producto ID", "Cantidad", "Precio Unit.", "Subtotal", "Ganancia"]]
    for d in venta.detalles:
        items_data.append([
            str(d.producto_id),
            str(d.cantidad),
            f"$ {d.precio_unitario:,.2f}",
            f"$ {d.subtotal:,.2f}",
            f"$ {d.ganancia_linea:,.2f}",
        ])

    tabla_items = Table(items_data, colWidths=[3*cm, 3*cm, 4*cm, 4*cm, 3*cm])
    tabla_items.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0), HEADER_COLOR),
        ("TEXTCOLOR",      (0, 0), (-1, 0), colors.white),
        ("FONTNAME",       (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("GRID",           (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("PADDING",        (0, 0), (-1, -1), 5),
    ]))
    elementos.append(tabla_items)
    elementos.append(Spacer(1, 0.5 * cm))

    # Totales
    totales_data = [
        ["TOTAL VENTA",   f"$ {venta.total_calculado:,.2f}"],
        ["GANANCIA NETA", f"$ {venta.ganancia_calculada:,.2f}"],
    ]
    tabla_totales = Table(totales_data, colWidths=[9*cm, 8*cm])
    tabla_totales.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#D6E4F0")),
        ("FONTNAME",   (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 11),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING",    (0, 0), (-1, -1), 7),
    ]))
    elementos.append(tabla_totales)

    doc.build(elementos)
    buffer.seek(0)
    return buffer.read()
