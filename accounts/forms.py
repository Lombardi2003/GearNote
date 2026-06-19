from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Profilo

class RegistrazionePersonalizzataForm(UserCreationForm):
    # 1. DICHIARA I CAMPI QUI (altrimenti Django non li vede)
    nome = forms.CharField(max_length=50, label="Nome")
    cognome = forms.CharField(max_length=50, label="Cognome")
    email = forms.EmailField(label="Email")
    eta = forms.IntegerField(label="Età")
    citta = forms.CharField(max_length=100, label="Città")
    
    # Definiamo le scelte per il ruolo (da far vedere nella tendina)
    RUOLI = [('acquirente', 'Acquirente'), ('venditore', 'Venditore')]
    ruolo = forms.ChoiceField(choices=RUOLI, label="Tipo di Account")
    
    foto_profilo = forms.ImageField(required=False, label="Foto Profilo")

    class Meta:
        model = User
        fields = ['username', 'email'] # Username è gestito da UserCreationForm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['nome']
        user.last_name = self.cleaned_data['cognome']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
            # Creazione Profilo
            ruolo_scelto = self.cleaned_data['ruolo']
            Profilo.objects.create(
                user=user, 
                eta=self.cleaned_data['eta'],
                citta=self.cleaned_data['citta'],
                ruolo=ruolo_scelto,
                foto_profilo=self.cleaned_data.get('foto_profilo')
            )

            # Assegnazione Gruppo
            nome_gruppo = ruolo_scelto.capitalize() 
            gruppo, _ = Group.objects.get_or_create(name=nome_gruppo)
            user.groups.add(gruppo)
            
        return user