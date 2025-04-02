from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Venta  # Asegúrate de que el modelo Venta está definido
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Venta, DetalleVenta, Cilindro, Cliente
from .forms import VentaForm, DetalleVentaForm, ClienteForm


@login_required
def lista_ventas(request):
    ventas = Venta.objects.all()  # Obtén todas las ventas

    # Agregar el cálculo de cantidad total de cilindros y precio total
    for venta in ventas:
        cantidad_total = sum(detalle.cantidad for detalle in venta.detalles.all())  # Suma de la cantidad de cilindros
        precio_total = sum(detalle.subtotal() for detalle in venta.detalles.all())  # Suma del precio total de los detalles

        venta.cantidad_total = cantidad_total
        venta.precio_total = precio_total

    return render(request, 'ventas/lista_ventas.html', {'ventas': ventas})

@login_required
def guardar_cliente(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        tipo_cliente = request.POST.get('tipo_cliente')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        direccion = request.POST.get('direccion')  # Capturamos la dirección

        cliente = Cliente.objects.create(
            nombre=nombre,
            tipo_cliente=tipo_cliente,
            telefono=telefono,
            email=email,
            direccion=direccion  # Guardamos la dirección
        )

        return JsonResponse({
            'success': True,
            'id': cliente.id,
            'nombre': cliente.nombre,
            'direccion': cliente.direccion  # Enviamos también la dirección en la respuesta
        })
    return JsonResponse({'success': False})

@login_required
def registrar_venta(request):
    if request.method == 'POST':
        venta_form = VentaForm(request.POST)
        detalle_form = DetalleVentaForm(request.POST)
        
        if venta_form.is_valid() and detalle_form.is_valid():
            # Crear la venta
            venta = venta_form.save(commit=False)
            venta.save()  # Guardamos la venta
            
            # Crear el detalle de la venta
            detalle = detalle_form.save(commit=False)
            detalle.venta = venta
            detalle.save()  # Guardamos el detalle de la venta

            # Actualizar stock del cilindro
            cilindro = detalle.cilindro
            cilindro.stock -= detalle.cantidad
            cilindro.save()

            return redirect('ventas:lista_ventas')  # Redirigir a la lista de ventas
    else:
        venta_form = VentaForm()
        detalle_form = DetalleVentaForm()

    return render(request, 'ventas/registrar_venta.html', {
        'venta_form': venta_form,
        'detalle_form': detalle_form
    })

@login_required
def detalle_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    return render(request, 'ventas/detalle_venta.html', {'venta': venta})

@login_required
def reporte_stock_pdf(request):
    # Obtener el stock de cilindros
    cilindros = Cilindro.objects.all()
    umbral_bajo = 5  # Umbral mínimo de alerta

    # Configurar el PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "Reporte de Stock de Cilindros")

    # Encabezado de la tabla
    data = [["Peso (kg)", "Stock", "Estado"]]

    # Llenar la tabla con datos
    for cilindro in cilindros:
        estado = "Bajo stock ⚠️" if cilindro.stock < umbral_bajo else "Suficiente"
        data.append([f"{cilindro.peso} kg", cilindro.stock, estado])

    # Crear la tabla
    table = Table(data, colWidths=[100, 100, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Posición de la tabla en el PDF
    table.wrapOn(c, 50, 600)
    table.drawOn(c, 50, 650)

    # Finalizar el PDF
    c.showPage()
    c.save()
    
    # Responder con el archivo PDF
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_stock.pdf"'
    return response