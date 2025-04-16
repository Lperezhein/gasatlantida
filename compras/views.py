from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Compra, DetalleCompra  # Asegúrate de que el modelo Compra está definido
from django.http import HttpResponse
from ventas.models import Cilindro
from .forms import CompraForm, DetalleCompraForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Proveedor


@login_required
def lista_compras(request):
    compras_list = Compra.objects.all().order_by('-fecha')  # ordena si quieres
    paginator = Paginator(compras_list, 10)  # 10 compras por página

    page_number = request.GET.get('page')
    compras = paginator.get_page(page_number)

    return render(request, 'compras/lista_compras.html', {'compras': compras})
@login_required
def registrar_compra(request):
    return HttpResponse("Aquí irá el formulario de registro de compras.")

@login_required
def detalle_compra(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)
    detalles = DetalleCompra.objects.filter(compra=compra)  # Obtener todos los detalles asociados a la compra
    return render(request, 'compras/detalle_compra.html', {
        'compra': compra,
        'detalles': detalles  # Pasar los detalles de la compra
    })

@login_required
def realizar_compra(request):
    if request.method == 'POST':
        compra_form = CompraForm(request.POST)
        detalle_form = DetalleCompraForm(request.POST)
        
        if compra_form.is_valid() and detalle_form.is_valid():
            nuevo_proveedor_nombre = compra_form.cleaned_data.get('nuevo_proveedor')
            proveedor = compra_form.cleaned_data.get('proveedor')

            # 📌 Si se ingresa un nuevo proveedor, guardarlo primero
            if nuevo_proveedor_nombre:
                proveedor, created = Proveedor.objects.get_or_create(nombre=nuevo_proveedor_nombre)
            elif not proveedor:
                # Si no se selecciona un proveedor y no se ingresa uno nuevo, error
                compra_form.add_error('proveedor', 'Debes seleccionar o agregar un proveedor.')
                return render(request, 'compras/realizar_compra.html', {
                    'compra_form': compra_form,
                    'detalle_form': detalle_form,
                })

            # 📌 Ahora guardamos la compra con el proveedor correcto
            compra = compra_form.save(commit=False)
            compra.proveedor = proveedor  # Asignamos el proveedor correcto
            compra.save()

            # 📌 Guardar el detalle de la compra
            detalle = detalle_form.save(commit=False)
            detalle.compra = compra
            detalle.save()

            # 📌 Actualizar stock del cilindro
            detalle.cilindro.stock += detalle.cantidad
            detalle.cilindro.save()

            return redirect('compras:lista_compras')
    else:
        compra_form = CompraForm()
        detalle_form = DetalleCompraForm()

    return render(request, 'compras/realizar_compra.html', {
        'compra_form': compra_form,
        'detalle_form': detalle_form,
    })

@csrf_exempt
def agregar_proveedor(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', None)
        if nombre:
            proveedor, created = Proveedor.objects.get_or_create(nombre=nombre)
            return JsonResponse({'id': proveedor.id, 'nombre': proveedor.nombre, 'created': created})
    return JsonResponse({'error': 'Nombre inválido'}, status=400)