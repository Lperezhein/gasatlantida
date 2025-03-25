from django import forms
from .models import Compra, DetalleCompra, Proveedor
from ventas.models import Cilindro

class CompraForm(forms.ModelForm):
    nuevo_proveedor = forms.CharField(
        required=False,
        label="Nuevo Proveedor (Opcional)", 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Compra
        fields = ['proveedor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 📌 Asegurarse de que el dropdown de proveedores siempre esté actualizado
        self.fields['proveedor'].queryset = Proveedor.objects.all()

class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['cilindro', 'cantidad', 'precio_unitario']

    # Personalizar el desplegable de cilindros
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cilindro'].queryset = Cilindro.objects.all()