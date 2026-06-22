from django.contrib import admin
from .models import Categoria, Prodotto, ImmagineProdotto

# Permette di aggiungere immagini direttamente dalla pagina del prodotto!
class ImmagineProdottoInline(admin.TabularInline):
    model = ImmagineProdotto
    extra = 1

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nome',)} # Compila lo slug in automatico

@admin.register(Prodotto)
class ProdottoAdmin(admin.ModelAdmin):
    list_display = ('titolo', 'venditore', 'prezzo', 'condizione', 'disponibile', 'data_inserimento')
    list_filter = ('disponibile', 'categoria', 'condizione')
    search_fields = ('titolo', 'descrizione')
    inlines = [ImmagineProdottoInline]