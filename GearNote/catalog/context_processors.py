from .models import Categoria

def categorie_navbar(request):
    return {
        'categorie_principali': Categoria.objects.filter(categoria_padre__isnull=True)
    }