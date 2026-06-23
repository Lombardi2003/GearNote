from .models import Carrello

def contatore_carrello(request):
    conteggio = 0
    
    if request.user.is_authenticated and request.user.profilo.ruolo != 'venditore':
        try:
            carrello = Carrello.objects.get(utente=request.user)
            conteggio = carrello.numero_articoli
        except Carrello.DoesNotExist:
            conteggio = 0
            
    return {'cart_items_count': conteggio}