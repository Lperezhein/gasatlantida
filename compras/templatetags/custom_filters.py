# compras/templatetags/custom_filters.py

from django import template

# Se registra el filtro personalizado en Django
register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        # Multiplicamos el valor de 'value' por 'arg' (que son la cantidad y el precio unitario)
        return value * arg
    except (ValueError, TypeError):
        # Si hay un error (por ejemplo, si uno de los valores no es numérico), retornamos 0
        return 0
