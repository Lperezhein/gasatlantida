from django.urls import path
from . import views

app_name = 'ventas'  # Espacio de nombres para evitar conflictos de URLs

urlpatterns = [
    path('', views.lista_ventas, name='lista_ventas'),
    path('registrar/', views.registrar_venta, name='registrar_venta'),
    path('<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
]
