from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profilo

class RegistrazionePersonalizzataForm(UserCreationForm):
    RUOLI_SCELTA = (
        ('acquirente', 'Acquirente'),
        ('venditore', 'Venditore'),
    )

    # Sostituisci il blocco del ruolo con questo:
    ruolo = forms.ChoiceField(
        choices=RUOLI_SCELTA, 
        label="Tipo di Account", # <-- LA FRASE SI CAMBIA QUI
        widget=forms.Select() # Tolti gli stili forzati
    )
    
    # E aggiorna anche la foto profilo per avere un'etichetta più pulita:
    foto_profilo = forms.ImageField(label="Foto Profilo (Opzionale)", required=False)
    
    nome = forms.CharField(max_length=30, required=True)
    cognome = forms.CharField(max_length=30, required=True)
    eta = forms.IntegerField(label="Età", min_value=0, required=True)
    citta = forms.CharField(label="Città", max_length=100, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['ruolo', 'nome', 'cognome', 'eta', 'citta', 'username', 'email'] 

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['nome']
        user.last_name = self.cleaned_data['cognome']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Recuperiamo l'immagine dal form compilato
            immagine = self.cleaned_data.get('foto_profilo')
            
            Profilo.objects.create(
                user=user, 
                eta=self.cleaned_data['eta'],
                citta=self.cleaned_data['citta'],
                ruolo=self.cleaned_data['ruolo'],
                foto_profilo=immagine # Salviamo l'immagine nel profilo
            )
        return user