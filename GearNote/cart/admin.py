from django.contrib import admin
from .models import Carrello, ElementoCarrello, Ordine, ElementoOrdine

admin.site.register(Carrello)
admin.site.register(ElementoCarrello)
# Aggiungi queste due righe per vedere gli ordini nel pannello admin:
admin.site.register(Ordine)
admin.site.register(ElementoOrdine)