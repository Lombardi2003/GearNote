from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import RegistrazionePersonalizzataForm, ModificaProfiloForm
from .models import Profilo
from catalog.models import Prodotto
from cart.models import Ordine, ElementoOrdine

from django.contrib.auth.models import User
from django.contrib import messages
from .models import Recensione
from .forms import RecensioneForm


# --- VISTA LOGIN ---
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True 

    def get_success_url(self):
        if self.request.user.is_superuser:
            return '/admin/'
        return reverse_lazy('accounts:profilo')


# --- VISTA REGISTRAZIONE ---
def registrazione_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profilo')

    if request.method == 'POST':
        form = RegistrazionePersonalizzataForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:profilo')
    else:
        form = RegistrazionePersonalizzataForm()
        
    return render(request, 'accounts/dati_profilo.html', {'form': form})


# --- VISTA LOGOUT ---
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/')

# --- VISTA PROFILO ---
@login_required(login_url='accounts:login')
def profilo_view(request):
    profilo, created = Profilo.objects.get_or_create(user=request.user)
    
    prodotti_utente = Prodotto.objects.filter(venditore=request.user)

    # 2. METODO INFALLIBILE: Conta quante volte un tuo prodotto è finito in un ordine confermato
    numero_vendite = ElementoOrdine.objects.filter(prodotto__venditore=request.user).count()

    miei_ordini = Ordine.objects.filter(utente=request.user).order_by('-creato_il')
    

    recensioni_ricevute = Recensione.objects.filter(venditore=request.user).order_by('-data_creazione')

    return render(request, 'accounts/profilo.html', {
        'profilo': profilo,           
        'miei_prodotti': prodotti_utente,
        'miei_ordini': miei_ordini,
        'numero_vendite': numero_vendite,
        'recensioni_ricevute': recensioni_ricevute, 
    })
# --- VISTA MODIFICA PROFILO ---
@login_required
def modifica_profilo(request):
    if request.method == 'POST':
        form = ModificaProfiloForm(request.POST, request.FILES, instance=request.user.profilo)
        if form.is_valid():
            form.save()
            return redirect('accounts:profilo')
    else:
        form = ModificaProfiloForm(instance=request.user.profilo)
    
    return render(request, 'accounts/dati_profilo.html', {'form': form})

@login_required
def disattiva_account(request):
    if request.method == 'POST':
        user = request.user
        user.is_active = False 
        user.save()
        
        logout(request)
        
        return redirect('/') 
    
    return redirect('accounts:profilo')

@login_required(login_url='accounts:login')
def recensione(request, venditore_id):
    venditore = get_object_or_404(User, id=venditore_id)

    if request.method == 'POST':
        form = RecensioneForm(request.POST)
        if form.is_valid():
            nuova_recensione = form.save(commit=False)
            nuova_recensione.acquirente = request.user
            nuova_recensione.venditore = venditore
            nuova_recensione.save()
            
            messages.success(request, f"Hai recensito {venditore.username} con successo!")
            return redirect('accounts:profilo')
    else:
        form = RecensioneForm()

    return render(request, 'accounts/recensione.html', {'form': form, 'venditore': venditore})