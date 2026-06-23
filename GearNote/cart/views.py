from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from catalog.models import Prodotto
from .models import Carrello, ElementoCarrello, Ordine, ElementoOrdine
from django.db import transaction
        


@login_required(login_url='accounts:login')
def aggiungi_al_carrello(request):
    if request.method == 'POST':
        # 1. Sicurezza: Blocca i venditori
        if getattr(request.user, 'profilo', None) and request.user.profilo.ruolo == 'venditore':
            return redirect('catalog:lista') 

        # 2. Recupera il prodotto
        prodotto_id = request.POST.get('prodotto_id')
        prodotto = get_object_or_404(Prodotto, id=prodotto_id)

        # 3. Prende il carrello dell'utente
        carrello, created = Carrello.objects.get_or_create(utente=request.user)

        # 4. Aggiunge il prodotto al carrello
        elemento, elemento_creato = ElementoCarrello.objects.get_or_create(
            carrello=carrello, 
            prodotto=prodotto
        )

        # 5. FORZATURA ASSOLUTA: La quantità è sempre e solo 1.
        # Anche se l'utente clicca 100 volte, il database imposterà il valore a 1.
        elemento.quantita = 1
        elemento.save()

        # 6. Rimanda al carrello
        return redirect('cart:vedi_carrello')
        
    return redirect('catalog:lista')

@login_required(login_url='accounts:login')
def vedi_carrello(request):
    # Mostra la pagina del carrello dell'utente
    carrello, created = Carrello.objects.get_or_create(utente=request.user)
    return render(request, 'cart/carrello.html', {'carrello': carrello})


@login_required(login_url='accounts:login')
def rimuovi_dal_carrello(request):
    if request.method == 'POST':
        elemento_id = request.POST.get('elemento_id')
        
        elemento = get_object_or_404(ElementoCarrello, id=elemento_id, carrello__utente=request.user)
        
        # Elimina la riga dal database
        elemento.delete()
        
    return redirect('cart:vedi_carrello')


from django.contrib import messages

@login_required(login_url='accounts:login')
def checkout(request):
    try:
        carrello = Carrello.objects.get(utente=request.user)
    except Carrello.DoesNotExist:
        return redirect('cart:vedi_carrello')

    elementi = carrello.elementi.all()

    if not elementi.exists():
        messages.error(request, "Il tuo carrello è vuoto.")
        return redirect('cart:vedi_carrello')

    if request.method == 'POST':
        # Controllo basico di lunghezza stringhe
        nome = request.POST.get('nome', '').strip()
        cap = request.POST.get('cap', '').strip()

        if len(nome) < 3 or len(cap) != 5:
            messages.error(request, "Per favore, controlla i dati inseriti (nome troppo corto o CAP non valido).")
            return render(request, 'cart/checkout.html', {'carrello': carrello})

        
        with transaction.atomic():
            ordine = Ordine.objects.create(
                utente=request.user,
                nome_completo=nome,
                indirizzo=request.POST.get('indirizzo', '').strip(),
                citta=request.POST.get('citta', '').strip(),
                cap=cap,
                totale=carrello.totale_carrello
            )

            for item in elementi:
                ElementoOrdine.objects.create(
                    ordine=ordine,
                    prodotto=item.prodotto,
                    prezzo_pagato=item.prodotto.prezzo
                )
                item.prodotto.disponibile = False
                item.prodotto.save()

            elementi.delete()

        return redirect('accounts:profilo')

    return render(request, 'cart/checkout.html', {'carrello': carrello})