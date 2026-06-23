from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Prodotto, Categoria, ImmagineProdotto
from .forms import ProdottoForm

# --- VISTA CATALOGO (Ricerca e Filtri) ---
def lista_prodotti(request):
    prodotti = Prodotto.objects.filter(disponibile=True)
    categorie = Categoria.objects.all() 

    # Logica dei filtri
    query_ricerca = request.GET.get('q')
    prezzo_min = request.GET.get('min_prezzo')
    prezzo_max = request.GET.get('max_prezzo')
    categoria_id = request.GET.get('categoria')

    if query_ricerca:
        prodotti = prodotti.filter(titolo__icontains=query_ricerca)
    if prezzo_min:
        prodotti = prodotti.filter(prezzo__gte=prezzo_min)
    if prezzo_max:
        prodotti = prodotti.filter(prezzo__lte=prezzo_max)
    if categoria_id:
        prodotti = prodotti.filter(categoria_id=categoria_id)

    context = {
        'prodotti': prodotti,
        'categorie': categorie, 
    }
    
    return render(request, 'catalog/lista.html', context)

# --- VISTA DETTAGLIO ---
def dettaglio_prodotto(request, id):
    prodotto = get_object_or_404(Prodotto, id=id)
    return render(request, 'catalog/prodotto.html', {'prodotto': prodotto})

# --- VISTA AGGIUNGI PRODOTTO ---
@login_required(login_url='/accounts/login/') 
def aggiungi_prodotto(request):
    if request.method == 'POST':
        form = ProdottoForm(request.POST, request.FILES)
        
        if form.is_valid():
            # 1. Mette in pausa il salvataggio
            prodotto = form.save(commit=False)
            
            # 2. Assegna il venditore loggato
            prodotto.venditore = request.user 
            
            # 3. Salva il prodotto base
            prodotto.save()
            
            # 4. SALVAVITA PER I TAG: Salva le relazioni molti-a-molti (come i Tag)
            form.save_m2m()
            
            # 5. Gestione foto multiple
            immagini = request.FILES.getlist('foto')
            for indice, file_immagine in enumerate(immagini):
                is_principale = True if indice == 0 else False
                ImmagineProdotto.objects.create(
                    prodotto=prodotto, 
                    immagine=file_immagine, 
                    principale=is_principale
                )
            
            # 6. Torna all'area personale
            return redirect('accounts:profilo') 
    else:
        form = ProdottoForm()

    # PUNTA AL NUOVO TEMPLATE UNIFICATO
    return render(request, 'catalog/dati_prodotto.html', {'form': form})

# --- VISTA MODIFICA PRODOTTO ---
@login_required(login_url='/accounts/login/')
def modifica_prodotto(request, prodotto_id):
    # Recupera il prodotto solo se appartiene all'utente loggato
    prodotto = get_object_or_404(Prodotto, id=prodotto_id, venditore=request.user)
    
    if request.method == 'POST':
        form = ProdottoForm(request.POST, request.FILES, instance=prodotto)
        if form.is_valid():
            prodotto_salvato = form.save() # Aggiorna titolo, prezzo, ecc.
            
            # --- AGGIUNTA LOGICA FOTO ---
            # Controlliamo se l'utente ha inserito dei nuovi file nel campo 'foto'
            nuove_immagini = request.FILES.getlist('foto')
            
            if nuove_immagini:
                # 1. Eliminiamo le vecchie foto dal database per evitare doppioni vecchi
                prodotto.immagini.all().delete()
                
                # 2. Salviamo le nuove foto appena caricate (stesso ciclo dell'inserimento)
                for indice, file_immagine in enumerate(nuove_immagini):
                    is_principale = True if indice == 0 else False
                    ImmagineProdotto.objects.create(
                        prodotto=prodotto_salvato, 
                        immagine=file_immagine, 
                        principale=is_principale
                    )
            
            return redirect('accounts:profilo') 
    else:
        form = ProdottoForm(instance=prodotto)
        
    return render(request, 'catalog/dati_prodotto.html', {
        'form': form,
        'prodotto': prodotto
    })

# --- VISTA ELIMINA PRODOTTO ---
@login_required(login_url='/accounts/login/')
def elimina_prodotto(request, prodotto_id):
    # Recupera il prodotto solo se appartiene all'utente loggato
    prodotto = get_object_or_404(Prodotto, id=prodotto_id, venditore=request.user)
    
    if request.method == 'POST':
        prodotto.delete() # Cancella definitivamente dal database
        return redirect('accounts:profilo')
        
    # PUNTA AL TUO FILE ELIMINA.HTML
    return render(request, 'catalog/elimina.html', {'prodotto': prodotto})