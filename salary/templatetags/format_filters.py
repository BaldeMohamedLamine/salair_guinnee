from django import template

register = template.Library()

@register.filter
def format_number(value):
    """Formate un nombre avec des espaces pour la lisibilité (ex: 1000000 -> 1 000 000)"""
    if value is None:
        return "0"
    
    # Convertir en entier et formater
    try:
        num = int(float(value))
        return f"{num:,}".replace(",", " ")
    except (ValueError, TypeError):
        return str(value)

@register.filter
def format_currency(value):
    """Formate un nombre avec des espaces et ajoute 'GNF'"""
    formatted = format_number(value)
    return f"{formatted} GNF"

@register.filter
def abs_value(value):
    """Retourne la valeur absolue d'un nombre"""
    if value is None:
        return 0
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0
