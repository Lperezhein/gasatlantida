from django.urls import path
from . import views
from .views import realizar_compra, lista_compras, agregar_proveedor  # Asegúrate de importar esto

app_name = 'compras'  # Espacio de nombres para evitar conflictos de URLs

urlpatterns = [
    path('', views.lista_compras, name='lista_compras'),
    path('registrar/', views.realizar_compra, name='registrar_compra'),
    path('<int:compra_id>/', views.detalle_compra, name='detalle_compra'),
    path('realizar/', views.realizar_compra, name='realizar_compra'),
    path('agregar_proveedor/', agregar_proveedor, name='agregar_proveedor'),  # Nueva URL
]
