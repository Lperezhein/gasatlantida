from django.db import models

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre# Create your models here.
    
class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Compra {self.id} - {self.proveedor.nombre} ({self.fecha})"

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="detalles")
    cilindro = models.ForeignKey("ventas.Cilindro", on_delete=models.CASCADE)  # Relación con ventas
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)