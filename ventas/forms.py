from django import forms
from .models import Venta, DetalleVenta, Cliente

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente']  # Mantén solo el cliente en este formulario

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['cilindro', 'cantidad', 'precio_unitario']

class ClienteForm(forms.ModelForm):  # Agregamos este formulario para manejar el cliente con dirección
    class Meta:
        model = Cliente
        fields = ['nombre', 'tipo_cliente', 'telefono', 'email', 'direccion']  # Incluimos el campo 'direccion'
