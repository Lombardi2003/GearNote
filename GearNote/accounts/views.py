from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import RegistrazionePersonalizzataForm, ModificaProfiloForm
from catalog.models import Prodotto

# --- VISTA LOGIN PERSONALIZZATA (Smistamento Admin / Utenti) ---
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    # Se uno è già loggato e va su /login/, lo rimbalziamo via
    redirect_authenticated_user = True 

    def get_success_url(self):
        # Se chi ha fatto l'accesso è un Superuser (Admin)...
        if self.request.user.is_superuser:
            return '/admin/'  # ...va direttamente al pannello di controllo
        # Altrimenti, è un utente normale e va al suo profilo
        return reverse_lazy('accounts:profilo')


# --- VISTA REGISTRAZIONE ---
# Cerca questa funzione dentro accounts/views.py e aggiorna solo questa riga:
def registrazione_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profilo')

    if request.method == 'POST':
        # REGOLA D'ORO: Aggiungi request.FILES come secondo argomento!
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
    # 1. Interroghiamo il database: prendi i prodotti dove il venditore è l'utente loggato
    prodotti_utente = Prodotto.objects.filter(venditore=request.user)
    
    return render(request, 'accounts/profilo.html', {
        'profilo': request.user.profilo,
        'miei_prodotti': prodotti_utente, # 2. PASSIAMO I PRODOTTI ALL'HTML!
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
        # Il "Soft Delete": l'utente esiste ancora nel DB ma è disattivato
        user.is_active = False 
        user.save()
        
        # Facciamo il logout automatico
        logout(request)
        
        # Rimandiamo alla pagina principale
        return redirect('/') 
    
    # Se qualcuno prova ad accedere tramite URL diretto (GET), lo rimandiamo al profilo
    return redirect('accounts:profilo')