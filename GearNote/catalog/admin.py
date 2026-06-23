from django.contrib import admin
from .models import Categoria, Condizione, Prodotto, ImmagineProdotto # <--- Nota: qui c'è Condizione, non più Tag

# --- 1. CONFIGURAZIONE CATEGORIE ---
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria_padre', 'slug')
    prepopulated_fields = {'slug': ('nome',)} 
    list_filter = ('categoria_padre',)
    search_fields = ('nome',)

# --- 2. CONFIGURAZIONE CONDIZIONE (Sostituisce i Tag) ---
@admin.register(Condizione)
class CondizioneAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

# --- 3. CONFIGURAZIONE PRODOTTI ---
class ImmagineProdottoInline(admin.TabularInline):
    model = ImmagineProdotto
    extra = 1

@admin.register(Prodotto)
class ProdottoAdmin(admin.ModelAdmin):
    list_display = ('titolo', 'prezzo', 'categoria', 'condizione', 'venditore', 'disponibile')
    list_filter = ('disponibile', 'categoria', 'condizione')
    search_fields = ('titolo', 'descrizione')
    
    inlines = [ImmagineProdottoInline]