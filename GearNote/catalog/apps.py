import os
import json
from django.apps import AppConfig
from django.db.models.signals import post_migrate

def popola_catalog_da_json(sender, **kwargs):
    """Legge i file JSON e popola automaticamente Condizioni e Categorie nel DB"""
    from .models import Categoria, Condizione
    from django.utils.text import slugify

    cartella_app = os.path.dirname(__file__)

    # --- 1. POPOLAMENTO CONDIZIONI ---
    percorso_condizioni = os.path.join(cartella_app, 'condizioni.json')
    
    if os.path.exists(percorso_condizioni):
        with open(percorso_condizioni, 'r', encoding='utf-8') as f:
            lista_condizioni = json.load(f)
        
        for nome_condizione in lista_condizioni:
            # get_or_create garantisce che non vengano creati duplicati nei migrate successivi
            Condizione.objects.get_or_create(nome=nome_condizione)


    # --- 2. POPOLAMENTO CATEGORIE ---
    percorso_categorie = os.path.join(cartella_app, 'categorie.json')
    
    if os.path.exists(percorso_categorie):
        with open(percorso_categorie, 'r', encoding='utf-8') as f:
            albero_categorie = json.load(f)

        def genera_slug_sicuro(nome):
            slug_base = slugify(nome)
            slug = slug_base
            contatore = 1
            while Categoria.objects.filter(slug=slug).exists():
                slug = f"{slug_base}-{contatore}"
                contatore += 1
            return slug

        # Ciclo Livello 1: Macro-Categorie
        for item_macro in albero_categorie:
            nome_macro = item_macro["macro"]
            macro, _ = Categoria.objects.get_or_create(
                nome=nome_macro, 
                categoria_padre=None,
                defaults={'slug': genera_slug_sicuro(nome_macro)}
            )

            # Ciclo Livello 2: Categorie Figlie
            for item_cat in item_macro.get("categorie", []):
                nome_cat = item_cat["nome"]
                cat, _ = Categoria.objects.get_or_create(
                    nome=nome_cat, 
                    categoria_padre=macro,
                    defaults={'slug': genera_slug_sicuro(nome_cat)}
                )

                # Ciclo Livello 3: Sottocategorie (Nipoti)
                for nome_sub in item_cat.get("sottocategorie", []):
                    Categoria.objects.get_or_create(
                        nome=nome_sub, 
                        categoria_padre=cat,
                        defaults={'slug': genera_slug_sicuro(nome_sub)}
                    )


class CatalogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalog'

    def ready(self):
        # Collega la funzione di setup globale al segnale post_migrate
        post_migrate.connect(popola_catalog_da_json, sender=self)