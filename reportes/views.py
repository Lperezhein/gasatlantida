from django.core.paginator import Paginator
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
from .models import Inventario  # Asegúrate de importar el modelo correctamente


@login_required
def reporte_panel(request):
    return render(request, 'reportes/reportes.html')


@login_required
def reporte_ventas(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    cliente_id = request.GET.get('cliente', '')
    tipo_cliente = request.GET.get('tipo_cliente', '')

    clientes = Cliente.objects.all()
    if tipo_cliente:
        clientes = clientes.filter(tipo_cliente=tipo_cliente)

    ventas = Venta.objects.all()

    if fecha_inicio and fecha_fin:
        try:
            ventas = ventas.filter(fecha__range=[fecha_inicio, fecha_fin])
        except ValueError:
            fecha_inicio, fecha_fin = '', ''

    if cliente_id:
        ventas = ventas.filter(cliente_id=cliente_id)

    if tipo_cliente:
        tipo_cliente = tipo_cliente.capitalize()
        ventas = ventas.filter(cliente__tipo_cliente=tipo_cliente)

    ventas = ventas.annotate(
        monto=Sum(
            ExpressionWrapper(
                F('detalles__cantidad') * F('detalles__precio_unitario'),
                output_field=DecimalField()
            )
        )
    )

    total_ventas = ventas.aggregate(total=Sum('monto'))['total'] or 0

    # ✅ PAGINACIÓN
    paginator = Paginator(ventas, 10)  # 10 resultados por página
    page = request.GET.get('page')
    ventas_page = paginator.get_page(page)

    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'cliente_seleccionado': int(cliente_id) if cliente_id else '',
        'clientes': clientes,
        'ventas': ventas_page,
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

    # Filtrar las ventas según los parámetros
    ventas = Venta.objects.all()

    if fecha_inicio:
        ventas = ventas.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        ventas = ventas.filter(fecha__lte=fecha_fin)
    if cliente and cliente != "Todos los clientes":
        ventas = ventas.filter(cliente__id=cliente)
    if tipo_cliente and tipo_cliente != "Todos los tipos":
        ventas = ventas.filter(cliente__tipo_cliente=tipo_cliente)

    ventas = ventas.annotate(
        monto=Sum(ExpressionWrapper(F('detalles__cantidad') * F('detalles__precio_unitario'), output_field=DecimalField()))
    )

    total_ventas = ventas.aggregate(total=Sum('monto'))['total'] or 0
    usuario = request.user.get_full_name() or request.user.username
    fecha_emision = datetime.now().strftime("%d/%m/%Y")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.pdf"'

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Logo
    logo_path = "core/static/img/logogas.png"  # Ruta del logo
    c.drawImage(logo_path, 50, 730, width=100, height=50)

    # Título y detalles
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 700, "Reporte de Ventas")  # Mover el título hacia abajo

    c.setFont("Helvetica", 10)
    c.drawString(400, 730, f"Fecha emisión: {fecha_emision}")
    c.drawString(400, 715, f"Generado por: {usuario}")

    # Filtros
    c.setFont("Helvetica", 12)
    c.drawString(400, 690, f"Fecha inicio: {fecha_inicio or 'Todos'}")
    c.drawString(400, 675, f"Fecha fin: {fecha_fin or 'Todos'}")
    c.drawString(400, 660, f"Tipo de Cliente: {tipo_cliente or 'Todos los tipos'}")

    # Tabla
    data = [['Fecha', 'Cliente', 'Monto']]
    for venta in ventas:
        data.append([
            venta.fecha.strftime("%d/%m/%Y"),
            venta.cliente.nombre,
            f"${venta.monto:.2f}"
        ])

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

    # Posición inicial para la tabla
    y_position = 690

    # Verificar si la tabla cabe en la página, si no, agregar una nueva página
    if y_position - len(data) * 20 < 50:
        c.showPage()  # Salto de página
        y_position = 690  # Reseteamos la posición en la nueva página

    table.wrapOn(c, 50, y_position)
    table.drawOn(c, 50, y_position - len(data) * 20)  # Dibuja la tabla ajustada a la posición

    # Total de ventas
    total_y_position = y_position - len(data) * 20 - 20  # 20 puntos debajo de la tabla
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, total_y_position, f"Total de Ventas: ${total_ventas:.2f}")

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

    total_compras = compras.aggregate(total=Sum('monto'))['total'] or 0
    fecha_emision = datetime.now().strftime("%d/%m/%Y")
    usuario = request.user.get_full_name() or request.user.username

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_compras.pdf"'

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Logo
    logo_path = "core/static/img/logogas.png"  # Ruta del logo
    c.drawImage(logo_path, 50, 730, width=100, height=50)

    # Título y detalles
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 700, "Reporte de Compras")  # Mover el título hacia abajo

    c.setFont("Helvetica", 10)
    c.drawString(400, 730, f"Fecha emisión: {fecha_emision}")
    c.drawString(400, 715, f"Generado por: {usuario}")

    # Filtros
    c.setFont("Helvetica", 12)
    c.drawString(400, 690, f"Fecha inicio: {fecha_inicio or 'Todos'}")
    c.drawString(400, 675, f"Fecha fin: {fecha_fin or 'Todos'}")

    # Tabla
    data = [["ID", "Proveedor", "Fecha", "Cilindros", "Total"]]
    for compra in compras:
        cilindros = "\n".join([f"{detalle.cantidad} cilindros de {detalle.cilindro.peso} kg" for detalle in compra.detalles.all()])
        data.append([compra.id, compra.proveedor.nombre, str(compra.fecha), cilindros, f"${compra.monto:.0f}"])

    table = Table(data, colWidths=[50, 120, 80, 150, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # Posición inicial para la tabla
    y_position = 660

    # Verificar si la tabla cabe en la página, si no, agregar una nueva página
    if y_position - len(data) * 20 < 50:
        c.showPage()  # Salto de página
        y_position = 690  # Reseteamos la posición en la nueva página

    table.wrapOn(c, 50, y_position)
    table.drawOn(c, 50, y_position - len(data) * 20)  # Dibuja la tabla ajustada a la posición

    # Total de compras
    total_y_position = y_position - len(data) * 20 - 20  # 20 puntos debajo de la tabla
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, total_y_position, f"Total de Compras: ${total_compras:.2f}")

    c.showPage()
    c.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response

@login_required
def reporte_stock_pdf(request):
    pass

@login_required
def reporte_inventario(request):
    # Recoger parámetros de filtro (si los hay)
    fecha_inicio = request.GET.get('fecha_inicio', datetime.now().date())
    fecha_fin = request.GET.get('fecha_fin', datetime.now().date())

    # Obtener las ventas en el periodo
    ventas = DetalleVenta.objects.filter(venta__fecha__range=[fecha_inicio, fecha_fin])
    
    # Sumar la cantidad de cilindros vendidos
    total_ventas = ventas.aggregate(total_ventas=Sum('cantidad'))['total_ventas'] or 0

    # Obtener las compras en el periodo
    compras = DetalleCompra.objects.filter(compra__fecha__range=[fecha_inicio, fecha_fin])
    
    # Sumar la cantidad de cilindros comprados
    total_compras = compras.aggregate(total_compras=Sum('cantidad'))['total_compras'] or 0

    # Supón que el stock inicial es 0 o puedes ajustarlo según tu caso
    stock_inicial = 0  # Cambia este valor si hay un stock inicial

    # Calcular el stock actual
    stock_actual = stock_inicial + total_compras - total_ventas

    # Preparar el contexto para la plantilla
    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total_compras': total_compras,
        'total_ventas': total_ventas,
        'stock_actual': stock_actual,
    }

    return render(request, 'reportes/reporte_inventario.html', context)

@login_required
def reporte_rentabilidad(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    compras = Compra.objects.all()
    ventas = Venta.objects.all()

    # Filtrado por fecha
    if fecha_inicio and fecha_fin:
        compras = compras.filter(fecha__range=[fecha_inicio, fecha_fin])
        ventas = ventas.filter(fecha__range=[fecha_inicio, fecha_fin])

    # Cálculo del monto total de compras
    compras = compras.annotate(
        monto=Sum(ExpressionWrapper(F('detalles__cantidad') * F('detalles__precio_unitario'), output_field=DecimalField()))
    )
    total_compras = compras.aggregate(total=Sum('monto'))['total'] or 0

    # Cálculo del monto total de ventas
    ventas = ventas.annotate(
        monto=Sum(ExpressionWrapper(F('detalles__cantidad') * F('detalles__precio_unitario'), output_field=DecimalField()))
    )
    total_ventas = ventas.aggregate(total=Sum('monto'))['total'] or 0

    # Cálculo de rentabilidad
    rentabilidad = total_ventas - total_compras

    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total_compras': total_compras,
        'total_ventas': total_ventas,
        'rentabilidad': rentabilidad,
    }

    # Si se solicita el PDF
    if 'pdf' in request.GET:
        # Crear respuesta HTTP para el PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_rentabilidad.pdf"'

        # Crear el PDF usando ReportLab
        c = canvas.Canvas(response, pagesize=letter)
        width, height = letter

        # Añadir título
        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, height - 50, "Reporte de Rentabilidad")

        # Añadir fechas
        c.setFont("Helvetica", 12)
        c.drawString(30, height - 100, f"Fecha de inicio: {fecha_inicio}")
        c.drawString(30, height - 120, f"Fecha de fin: {fecha_fin}")

        # Añadir información de rentabilidad
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, height - 150, f"Total Compras: ${total_compras:,.0f}")
        c.drawString(30, height - 170, f"Total Ventas: ${total_ventas:,.0f}")
        c.drawString(30, height - 190, f"Rentabilidad: ${rentabilidad:,.0f}")

        # Añadir tabla con los detalles
        c.setFont("Helvetica", 10)
        c.drawString(30, height - 230, "Descripción")
        c.drawString(250, height - 230, "Monto")

        y_position = height - 250
        data = [
            ("Compras", total_compras),
            ("Ventas", total_ventas),
            ("Rentabilidad", rentabilidad)
        ]

        for item in data:
            c.drawString(30, y_position, item[0])
            c.drawString(250, y_position, f"${item[1]:,.0f}")
            y_position -= 20

        # Guardar el PDF
        c.showPage()
        c.save()

        return response

    # Si no se solicita PDF, renderizamos el reporte normal
    return render(request, 'reportes/reporte_rentabilidad.html', context)

@login_required
def reporte_rentabilidad_pdf(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    # Obtiene las compras y ventas dentro del rango de fechas
    compras = Compra.objects.all()
    ventas = Venta.objects.all()

    if fecha_inicio and fecha_fin:
        compras = compras.filter(fecha__range=[fecha_inicio, fecha_fin])
        ventas = ventas.filter(fecha__range=[fecha_inicio, fecha_fin])

    # Calcular el monto total de compras y ventas
    compras = compras.annotate(
        monto=Sum(ExpressionWrapper(F('detalles__cantidad') * F('detalles__precio_unitario'), output_field=DecimalField()))
    )
    total_compras = compras.aggregate(total=Sum('monto'))['total'] or 0

    ventas = ventas.annotate(
        monto=Sum(ExpressionWrapper(F('detalles__cantidad') * F('detalles__precio_unitario'), output_field=DecimalField()))
    )
    total_ventas = ventas.aggregate(total=Sum('monto'))['total'] or 0

    # Calcular la rentabilidad
    rentabilidad = total_ventas - total_compras
    rentabilidad_porc = ((total_ventas - total_compras)/total_compras)*100

    # Formatear rentabilidad_porc a dos decimales
    rentabilidad_porc = round(rentabilidad_porc, 2)

    # Fecha de emisión y usuario
    fecha_emision = datetime.now().strftime("%d/%m/%Y")
    usuario = request.user.get_full_name() or request.user.username

    # Configuración de la respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_rentabilidad.pdf"'

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Logo
    logo_path = "core/static/img/logogas.png"  # Ruta del logo
    c.drawImage(logo_path, 50, 730, width=100, height=50)

    # Título y detalles
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 700, "Reporte de Rentabilidad")  # Mover el título hacia abajo

    c.setFont("Helvetica", 10)
    c.drawString(400, 730, f"Fecha emisión: {fecha_emision}")
    c.drawString(400, 715, f"Generado por: {usuario}")

    # Filtros
    c.setFont("Helvetica", 12)
    c.drawString(400, 690, f"Fecha inicio: {fecha_inicio or 'Todos'}")
    c.drawString(400, 675, f"Fecha fin: {fecha_fin or 'Todos'}")

    # Rentabilidad calculada
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 650, f"Total Compras: ${total_compras:,.0f}")
    c.drawString(50, 635, f"Total Ventas: ${total_ventas:,.0f}")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 620, f"Rentabilidad: ${rentabilidad:,.0f}")
    c.drawString(50, 605, f"Rentabilidad porcentual: {rentabilidad_porc:.2f}%")

    # Tabla con los datos de compras y ventas
    data = [
        ["Concepto", "Monto ($)"],
        ["Compras", total_compras],
        ["Ventas", total_ventas],
        ["Rentabilidad", rentabilidad],
        ["Rentabilidad Porcentual", rentabilidad_porc]
    ]

    table = Table(data, colWidths=[150, 100])
    table.setStyle(TableStyle([  
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # Posición inicial para la tabla
    y_position = 580

    # Verificar si la tabla cabe en la página, si no, agregar una nueva página
    if y_position - len(data) * 20 < 50:
        c.showPage()  # Salto de página
        y_position = 690  # Reseteamos la posición en la nueva página

    table.wrapOn(c, 50, y_position)
    table.drawOn(c, 50, y_position - len(data) * 20)  # Dibuja la tabla ajustada a la posición

    # Finalizamos la página
    c.showPage()
    c.save()

    # Obtener el valor del buffer y enviarlo como respuesta
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response
