from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegistrazioneForm

def registrazione_view(request):
    if request.method == 'POST':
        form = RegistrazioneForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.profilo.ruolo = form.cleaned_data.get('ruolo')
            user.profilo.save()
            login(request, user)
            # Reindirizza direttamente alla pagina del profilo appena creata
            return redirect('accounts:profilo') 
    else:
        form = RegistrazioneForm()
        
    return render(request, 'accounts/registrazione.html', {'form': form})

# Protegge la vista: se non sei loggato, vieni rimandato al login
@login_required
def profilo_view(request):
    # request.user contiene già tutti i dati dell'utente autenticato
    return render(request, 'accounts/profilo.html')