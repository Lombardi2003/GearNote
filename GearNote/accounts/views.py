from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import RegistrazionePersonalizzataForm, ModificaProfiloForm
from .models import Profilo
from catalog.models import Prodotto
from cart.models import Ordine 


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

    miei_ordini = Ordine.objects.filter(utente=request.user).order_by('-creato_il')
    
    return render(request, 'accounts/profilo.html', {
        'profilo': profilo,           
        'miei_prodotti': prodotti_utente,
        'miei_ordini': miei_ordini,
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