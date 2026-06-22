from django.shortcuts import render, get_object_or_404
from .models import Prodotto

def lista_prodotti(request):
    prodotti = Prodotto.objects.filter(disponibile=True)
    return render(request, 'catalog/lista.html', {'prodotti': prodotti})

def dettaglio_prodotto(request, id):
    prodotto = get_object_or_404(Prodotto, id=id)
    return render(request, 'catalog/prodotto.html', {'prodotto': prodotto})