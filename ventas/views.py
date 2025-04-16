from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Venta  # Asegúrate de que el modelo Venta está definido
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Venta, DetalleVenta, Cilindro, Cliente
from .forms import VentaForm, DetalleVentaForm, ClienteForm
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from compras.models import Compra, DetalleCompra
from datetime import datetime



@login_required
def lista_ventas(request):
    ventas_list = Venta.objects.all().order_by('-fecha')  # Ordenadas por fecha descendente
    paginator = Paginator(ventas_list, 10)  # 10 ventas por página
    page = request.GET.get('page')
    ventas_page = paginator.get_page(page)

    # Calcular los totales SOLO para las ventas que están en la página actual
    for venta in ventas_page:
        cantidad_total = sum(detalle.cantidad for detalle in venta.detalles.all())
        precio_total = sum(detalle.subtotal() for detalle in venta.detalles.all())

        venta.cantidad_total = cantidad_total
        venta.precio_total = precio_total

    return render(request, 'ventas/lista_ventas.html', {
        'ventas': ventas_page
    })

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
    pass