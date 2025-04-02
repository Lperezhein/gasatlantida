from django.urls import path
from . import views
from .views import reporte_ventas, reporte_compras, reporte_compras_pdf, reporte_panel, reporte_rentabilidad
from ventas.views import reporte_stock_pdf

app_name = 'reportes'  # Este es el namespace que se usa en los templates

urlpatterns = [
    path('ventas/', views.reporte_ventas, name='reporte_ventas'),
    path('generar_reporte_pdf/', views.generar_reporte_pdf, name='generar_reporte_pdf'),
    path('compras/', reporte_compras, name="reporte_compras"),
    path('compras/pdf/', reporte_compras_pdf, name="reporte_compras_pdf"),
    path('', reporte_panel, name="reporte_panel"),  # Página principal de los reportes
    path('inventario/', views.reporte_inventario, name='reporte_inventario'),  # Nueva URL
    path('rentabilidad/', reporte_rentabilidad, name='reporte_rentabilidad'),  # Agrega esta línea
]
