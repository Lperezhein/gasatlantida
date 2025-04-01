from django.db import models

class Cilindro(models.Model):
    peso = models.PositiveIntegerField(unique=True)  # kg
    stock = models.PositiveIntegerField(default=0)  # Cantidad en stock

    def __str__(self):
        return f"{self.peso} kg - Stock: {self.stock}"

class Cliente(models.Model):
    MAYORISTA = 'Mayorista'
    MINORISTA = 'Minorista'
    DOMICILIARIO = 'Domiciliario'
    
    TIPO_CLIENTE_CHOICES = [
        (MAYORISTA, 'Mayorista'),
        (MINORISTA, 'Minorista'),
        (DOMICILIARIO, 'Domiciliario'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo_cliente = models.CharField(max_length=20, choices=TIPO_CLIENTE_CHOICES)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)  # Campo para la dirección

    def __str__(self):
        return f"{self.nombre} ({self.tipo_cliente})"

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Venta {self.id} - {self.cliente.nombre} ({self.fecha})"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    cilindro = models.ForeignKey(Cilindro, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=1)

    def subtotal(self):
        return self.cantidad * self.precio_unitario