from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q  # <--- Serve per fare ricerche multiple (es. titolo OPPURE descrizione)
from .models import Prodotto, Categoria, ImmagineProdotto, Condizione  # <--- Rimosso Tag, aggiunto Condizione
from .forms import ProdottoForm

# --- VISTA CATALOGO (Ricerca e Filtri Dinamici) ---
def lista_prodotti(request):
    prodotti = Prodotto.objects.filter(disponibile=True)
    
    # 1. Recuperiamo le categorie principali (senza padre) per creare il menu a tendina laterale
    categorie_principali = Categoria.objects.filter(categoria_padre__isnull=True)
    
    # 2. Recuperiamo tutte le Condizioni dal DB
    condizioni = Condizione.objects.filter(prodotti__disponibile=True).distinct()
    # Logica dei filtri: leggiamo cosa c'è nell'URL (cosa ha cliccato l'utente)
    query_ricerca = request.GET.get('q')
    prezzo_min = request.GET.get('min_prezzo')
    prezzo_max = request.GET.get('max_prezzo')
    categoria_id = request.GET.get('categoria')
    condizione_id = request.GET.get('condizione') # <--- Sostituito tag_id con condizione_id

    # APPLICHIAMO I FILTRI AL DATABASE
    if query_ricerca:
        # Cerca la parola sia nel titolo che nella descrizione
        prodotti = prodotti.filter(Q(titolo__icontains=query_ricerca) | Q(descrizione__icontains=query_ricerca))
        
    if prezzo_min:
        prodotti = prodotti.filter(prezzo__gte=prezzo_min)
        
    if prezzo_max:
        prodotti = prodotti.filter(prezzo__lte=prezzo_max)
        
    if condizione_id:
        # Filtra i prodotti che hanno esattamente questa condizione (tramite ForeignKey)
        prodotti = prodotti.filter(condizione_id=condizione_id)

    if categoria_id:
        categoria_scelta = Categoria.objects.get(id=categoria_id)
        
        # Questa funzione prende la categoria scelta + tutte le figlie + tutte le nipoti
        def get_tutti_i_discendenti(cat):
            lista_ids = [cat.id]
            for sottocategoria in cat.sottocategorie.all():
                lista_ids.extend(get_tutti_i_discendenti(sottocategoria))
            return lista_ids

        tutti_gli_ids = get_tutti_i_discendenti(categoria_scelta)
        
        # Filtriamo usando __in (che accetta una lista di ID)
        prodotti = prodotti.filter(categoria__id__in=tutti_gli_ids)

    # Passiamo tutti i dati al template
    context = {
        'prodotti': prodotti,
        'categorie_principali': categorie_principali,
        'condizioni': condizioni,          # <--- Passiamo le condizioni
        'cat_selezionata': categoria_id,
        'cond_selezionata': condizione_id, # <--- Rimosso tag
        'q': query_ricerca,
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
            
            # 3. Salva il prodotto base (salva automaticamente anche la chiave esterna della Condizione)
            prodotto.save()
            
            # (Rimosso form.save_m2m() perché non abbiamo più i Tag molti-a-molti!)
            
            # 4. Gestione foto multiple
            immagini = request.FILES.getlist('foto')
            for indice, file_immagine in enumerate(immagini):
                is_principale = True if indice == 0 else False
                ImmagineProdotto.objects.create(
                    prodotto=prodotto, 
                    immagine=file_immagine, 
                    principale=is_principale
                )
            
            # 5. Torna all'area personale
            return redirect('accounts:profilo') 
    else:
        form = ProdottoForm()

    return render(request, 'catalog/dati_prodotto.html', {'form': form})


# --- VISTA MODIFICA PRODOTTO ---
@login_required(login_url='/accounts/login/')
def modifica_prodotto(request, prodotto_id):
    prodotto = get_object_or_404(Prodotto, id=prodotto_id, venditore=request.user)
    
    if request.method == 'POST':
        form = ProdottoForm(request.POST, request.FILES, instance=prodotto)
        if form.is_valid():
            prodotto_salvato = form.save()
            
            # --- 1. OPERAZIONE CHIRURGICA: RIMOZIONE DELLE FOTO SELEZIONATE ---
            foto_da_eliminare = request.POST.getlist('elimina_foto')
            if foto_da_eliminare:
                ImmagineProdotto.objects.filter(id__in=foto_da_eliminare, prodotto=prodotto).delete()
            
            # --- 2. OPERAZIONE ACCODO: AGGIUNTA DI NUOVE IMMAGINI ---
            nuove_immagini = request.FILES.getlist('foto')
            if nuove_immagini:
                ha_gia_foto = prodotto.immagini.exists()
                
                for indice, file_immagine in enumerate(nuove_immagini):
                    is_principale = True if (not ha_gia_foto and indice == 0) else False
                    ImmagineProdotto.objects.create(
                        prodotto=prodotto_salvato, 
                        immagine=file_immagine, 
                        principale=is_principale
                    )
            
            # --- 3. POLIZZA ASSICURATIVA SULLA COPERTINA ---
            if prima_foto := prodotto.immagini.first():
                if not prodotto.immagini.filter(principale=True).exists():
                    prima_foto.principale = True
                    prima_foto.save()
            
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
    prodotto = get_object_or_404(Prodotto, id=prodotto_id, venditore=request.user)
    
    if request.method == 'POST':
        prodotto.delete() 
        return redirect('accounts:profilo')
        
    return render(request, 'catalog/elimina.html', {'prodotto': prodotto})