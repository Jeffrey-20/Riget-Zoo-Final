
from django import template
register = template.Library() # this creates an instance of template.library

@register.filter  # It helps with selection of an item using the cart dictionary and key
def get_item(cart, key):
    return cart.get(str(key))

