from django.db import models

class Inventario(models.Model):
    producto = models.CharField(max_length=255)
    cantidad = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.producto} - {self.cantidad}"
