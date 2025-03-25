from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('registrar/', views.registrar_venta, name='registrar_venta'),
     path('guardar_cliente/', views.guardar_cliente, name='guardar_cliente'),  # Nueva URL para AJAX
    path('lista/', views.lista_ventas, name='lista_ventas'),
    path('detalle/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
]