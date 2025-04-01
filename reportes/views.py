from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ventas.models import Venta, Cliente, DetalleVenta
from datetime import datetime
from django.db.models import Sum
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from django.template.loader import render_to_string
from django.db.models import F, ExpressionWrapper, DecimalField
from django.db.models import F, ExpressionWrapper, DecimalField, Sum
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from compras.models import Compra, DetalleCompra
from django.db.models import Sum, F, ExpressionWrapper, DecimalField

@login_required
def reporte_panel(request):
    return render(request, 'reportes/reportes.html')


@login_required
def reporte_ventas(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    cliente_id = request.GET.get('cliente', '')
    tipo_cliente = request.GET.get('tipo_cliente', '')

    # Obtener todos los clientes
    clientes = Cliente.objects.all()

    # Filtrado por tipo de cliente (aplicado a clientes y luego a ventas)
    if tipo_cliente:
        clientes = clientes.filter(tipo_cliente=tipo_cliente)

    ventas = Venta.objects.all()

    # Filtrado por fecha
    if fecha_inicio and fecha_fin:
        try:
            ventas = ventas.filter(fecha__range=[fecha_inicio, fecha_fin])
        except ValueError:
            fecha_inicio, fecha_fin = '', ''

    # Filtrado por cliente
    if cliente_id:
        ventas = ventas.filter(cliente_id=cliente_id)

    # **AQUÍ SE APLICA EL FILTRO POR `tipo_cliente`**
    if tipo_cliente:
        tipo_cliente = tipo_cliente.capitalize()  # Convierte "mayorista" en "Mayorista"
        ventas = ventas.filter(cliente__tipo_cliente=tipo_cliente)


    # Cálculo del monto total de las ventas correctamente
    ventas = ventas.annotate(
        monto=Sum(ExpressionWrapper(F('detalles__cantidad') * F('detalles__precio_unitario'), output_field=DecimalField()))
    )

    total_ventas = ventas.aggregate(total=Sum('monto'))['total'] or 0

    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'cliente_seleccionado': int(cliente_id) if cliente_id else '',
        'clientes': clientes,
        'ventas': ventas,
        'total_ventas': total_ventas,
        'tipo_cliente': tipo_cliente
    }

    return render(request, 'reportes/reporte_ventas.html', context)


@login_required
def generar_reporte_pdf(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    cliente = request.GET.get('cliente')
    tipo_cliente = request.GET.get('tipo_cliente')

    ventas = Venta.objects.all()

    if fecha_inicio:
        ventas = ventas.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        ventas = ventas.filter(fecha__lte=fecha_fin)
    if cliente and cliente != "Todos los clientes":
        ventas = ventas.filter(cliente__id=cliente)
    if tipo_cliente and tipo_cliente != "Todos los tipos":
        ventas = ventas.filter(cliente__tipo_cliente=tipo_cliente)

    # Calcular montos correctamente
    ventas = ventas.annotate(
        monto=Sum(ExpressionWrapper(F('detalles__cantidad') * F('detalles__precio_unitario'), output_field=DecimalField()))
    )

    total_ventas = ventas.aggregate(total=Sum('monto'))['total'] or 0

    # Creación del PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.pdf"'

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Título del reporte
    c.setFont("Helvetica", 16)
    c.drawString(200, 750, "Reporte de Ventas")

    # Filtros en el reporte
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Fecha inicio: {fecha_inicio if fecha_inicio else 'Todos'}")
    c.drawString(50, 705, f"Fecha fin: {fecha_fin if fecha_fin else 'Todos'}")
    c.drawString(50, 690, f"Cliente: {cliente if cliente else 'Todos los clientes'}")
    c.drawString(50, 675, f"Tipo de Cliente: {tipo_cliente if tipo_cliente else 'Todos los tipos'}")

    # Crear tabla
    data = [['Fecha', 'Cliente', 'Monto']]
    for venta in ventas:
        data.append([
            venta.fecha.strftime("%d/%m/%Y"),
            venta.cliente.nombre,
            f"${venta.monto:.2f}"
        ])

    # Dibujar la tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    table.wrapOn(c, 50, 600)
    table.drawOn(c, 50, 550)

    # Total de ventas
    c.drawString(50, 500, f"Total de Ventas: ${total_ventas:.2f}")

    c.showPage()
    c.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response

@login_required
def reporte_compras(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    compras = Compra.objects.all()

    # Filtrar por fecha si se proporciona
    if fecha_inicio and fecha_fin:
        compras = compras.filter(fecha__range=[fecha_inicio, fecha_fin])

    # Cálculo del monto total de compras
    compras = compras.annotate(
        monto=Sum(ExpressionWrapper(F('detalles__cantidad') * F('detalles__precio_unitario'), output_field=DecimalField()))
    )

    total_compras = compras.aggregate(total=Sum('monto'))['total'] or 0

    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'compras': compras,
        'total_compras': total_compras
    }

    return render(request, 'reportes/reporte_compras.html', context)


@login_required
def reporte_compras_pdf(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    compras = Compra.objects.all()

    if fecha_inicio and fecha_fin:
        compras = compras.filter(fecha__range=[fecha_inicio, fecha_fin])

    compras = compras.annotate(
        monto=Sum(ExpressionWrapper(F('detalles__cantidad') * F('detalles__precio_unitario'), output_field=DecimalField()))
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Título
    elements.append(Table([[f"Reporte de Compras ({fecha_inicio} - {fecha_fin})"]], colWidths=[500]))

    # Encabezado de la tabla
    data = [["ID", "Proveedor", "Fecha", "Cilindros", "Total"]]

    for compra in compras:
        cilindros = "\n".join([f"{detalle.cantidad} cilindros de {detalle.cilindro.peso} kg" for detalle in compra.detalles.all()])
        data.append([compra.id, compra.proveedor.nombre, str(compra.fecha), cilindros, f"${compra.monto:.0f}"])

    # Estilo de la tabla
    tabla = Table(data, colWidths=[50, 120, 80, 150, 80])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(tabla)
    doc.build(elements)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_compras.pdf"'
    return response