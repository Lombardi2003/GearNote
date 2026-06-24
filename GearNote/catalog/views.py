from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q 
from .models import Prodotto, Categoria, ImmagineProdotto, Condizione  
from .forms import ProdottoForm
from django.contrib import messages

# --- VISTA CATALOGO (Ricerca e Filtri Dinamici) ---
def lista_prodotti(request, slug_categoria=None):
    prodotti = Prodotto.objects.filter(disponibile=True)
    categorie_principali = Categoria.objects.filter(categoria_padre__isnull=True)
    condizioni = Condizione.objects.filter(prodotti__disponibile=True).distinct()

    query_ricerca = request.GET.get('q')
    prezzo_min = request.GET.get('min_prezzo')
    prezzo_max = request.GET.get('max_prezzo')
    condizione_id = request.GET.get('condizione')

    if slug_categoria:
        categoria_scelta = get_object_or_404(Categoria, slug=slug_categoria)
        
        def get_tutti_i_discendenti(cat):
            lista_ids = [cat.id]
            for sottocategoria in cat.sottocategorie.all():
                lista_ids.extend(get_tutti_i_discendenti(sottocategoria))
            return lista_ids

        tutti_gli_ids = get_tutti_i_discendenti(categoria_scelta)
        prodotti = prodotti.filter(categoria__id__in=tutti_gli_ids)
        cat_selezionata_id = categoria_scelta.id                            # Per il template
    else:
        categoria_id = request.GET.get('categoria')
        cat_selezionata_id = int(categoria_id) if categoria_id else None
        if categoria_id:
            categoria_scelta = Categoria.objects.get(id=categoria_id)
    
    context = {
        'prodotti': prodotti,
        'categorie_principali': categorie_principali,
        'condizioni': condizioni,
        'cat_selezionata': cat_selezionata_id,
        'cond_selezionata': condizione_id,
        'q': query_ricerca,
    }
    return render(request, 'catalog/lista.html', context)

# --- VISTA DETTAGLIO ---
def dettaglio_prodotto(request, id):
    prodotto = get_object_or_404(Prodotto, id=id)
    return render(request, 'catalog/prodotto.html', {'prodotto': prodotto})


# --- VISTA AGGIUNGI PRODOTTO ---
# --- VISTA AGGIUNGI PRODOTTO ---
@login_required(login_url='/accounts/login/') 
def aggiungi_prodotto(request):
    
    # 🔒 BLOCCO DI SICUREZZA: Verifica che l'utente sia effettivamente un venditore
    if not hasattr(request.user, 'profilo') or request.user.profilo.ruolo != 'venditore':
        messages.error(request, "Accesso negato. Solo i venditori possono creare annunci.")
        return redirect('home') 
    
    if request.method == 'POST':
        form = ProdottoForm(request.POST, request.FILES)
        
        if form.is_valid():
            # 1. Mette in pausa il salvataggio
            prodotto = form.save(commit=False)
            
            # 2. Assegna il venditore loggato
            prodotto.venditore = request.user 
            
            # 3. Salva il prodotto base (salva automaticamente anche la chiave esterna della Condizione)
            prodotto.save()
                        
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
            
            foto_da_eliminare = request.POST.getlist('elimina_foto')
            if foto_da_eliminare:
                ImmagineProdotto.objects.filter(id__in=foto_da_eliminare, prodotto=prodotto).delete()
            
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


# --- VISTA HOMEPAGE ---
def home_view(request):
    prodotti_recenti = Prodotto.objects.filter(disponibile=True).order_by('-id')[:4]
    
    return render(request, 'home.html', {
        'prodotti_recenti': prodotti_recenti
    })