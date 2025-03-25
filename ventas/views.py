from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Venta  # Asegúrate de que el modelo Venta está definido
from django.http import HttpResponse

@login_required
def lista_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'ventas/lista_ventas.html', {'ventas': ventas})

@login_required
def registrar_venta(request):
    return HttpResponse("Aquí irá el formulario de registro de ventas.")

@login_required
def detalle_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    return render(request, 'ventas/detalle_venta.html', {'venta': venta})
