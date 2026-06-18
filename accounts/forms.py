from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profilo

class RegistrazionePersonalizzataForm(UserCreationForm):
    nome = forms.CharField(max_length=30, required=True)
    cognome = forms.CharField(max_length=30, required=True)
    eta = forms.IntegerField(label="Età", min_value=0, required=True)
    citta = forms.CharField(label="Città", max_length=100, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        # Le due password vengono aggiunte da Django automaticamente in fondo a questa lista
        fields = ['nome', 'cognome', 'eta', 'citta', 'username', 'email'] 

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['nome']
        user.last_name = self.cleaned_data['cognome']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Salviamo anche la città nel profilo
            Profilo.objects.create(
                user=user, 
                eta=self.cleaned_data['eta'],
                citta=self.cleaned_data['citta']
            )
        return user