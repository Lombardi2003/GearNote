from django.contrib import admin
from .models import Categoria, Prodotto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria_padre')
    search_fields = ('nome',)

@admin.register(Prodotto)
class ProdottoAdmin(admin.ModelAdmin):
    # Colonne visibili nella tabella riassuntiva
    list_display = ('titolo', 'categoria', 'strumento_riferimento', 'prezzo', 'venditore')
    # Crea in automatico la barra laterale destra con i filtri!
    list_filter = ('categoria', 'strumento_riferimento', 'condizione')
    search_fields = ('titolo', 'descrizione')