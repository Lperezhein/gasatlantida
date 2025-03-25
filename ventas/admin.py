from django.contrib import admin
from .models import Cliente, Venta, DetalleVenta, Cilindro

admin.site.register(Cliente)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(Cilindro)
