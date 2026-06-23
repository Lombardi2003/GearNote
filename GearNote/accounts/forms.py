import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Profilo
from django.conf import settings
import os
from .models import Recensione

class ValidazioneProfiloMixin:
    def clean_eta(self):
        eta = self.cleaned_data.get('eta')
        if eta is not None:
            if eta < 18:
                raise forms.ValidationError("Devi avere almeno 18 anni per usare GearNote.")
            if eta > 100:
                raise forms.ValidationError("Inserisci un'età valida (massimo 100 anni).")
        return eta

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if nome and not re.match(r"^[A-Za-zÀ-ÿ\s\']+$", nome):
            raise forms.ValidationError("Il nome può contenere solo lettere, spazi o apostrofi.")
        return nome

    def clean_cognome(self):
        cognome = self.cleaned_data.get('cognome')
        if cognome and not re.match(r"^[A-Za-zÀ-ÿ\s\']+$", cognome):
            raise forms.ValidationError("Il cognome contiene caratteri non validi.")
        return cognome
        
    def clean_citta(self):
        citta = self.cleaned_data.get('citta')
        if citta and len(citta) < 2:
            raise forms.ValidationError("Il nome della città è troppo corto.")
        return citta

class RegistrazionePersonalizzataForm(ValidazioneProfiloMixin, UserCreationForm):
    nome = forms.CharField(max_length=50, label="Nome", widget=forms.TextInput(attrs={'placeholder': 'Es. Mario'}))
    cognome = forms.CharField(max_length=50, label="Cognome", widget=forms.TextInput(attrs={'placeholder': 'Es. Rossi'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'placeholder': 'mario.rossi@email.com'}))
    eta = forms.IntegerField(label="Età", widget=forms.NumberInput(attrs={'min': '18', 'max': '100', 'placeholder': 'Es. 22'}))
    citta = forms.CharField(max_length=100, label="Città", widget=forms.TextInput(attrs={'placeholder': 'Es. Roma'}))
    
    RUOLI = [('acquirente', 'Acquirente'), ('venditore', 'Venditore')]
    ruolo = forms.ChoiceField(choices=RUOLI, label="Tipo di Account")
    foto_profilo = forms.ImageField(required=False, label="Foto Profilo")

    class Meta:
        model = User
        fields = ['username', 'email'] 

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['nome']
        user.last_name = self.cleaned_data['cognome']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
            ruolo_scelto = self.cleaned_data['ruolo']
            Profilo.objects.create(
                user=user, 
                eta=self.cleaned_data['eta'],
                citta=self.cleaned_data['citta'],
                ruolo=ruolo_scelto,
                foto_profilo=self.cleaned_data.get('foto_profilo')
            )

            nome_gruppo = ruolo_scelto.capitalize() 
            gruppo, _ = Group.objects.get_or_create(name=nome_gruppo)
            user.groups.add(gruppo)
            
        return user

class ModificaProfiloForm(ValidazioneProfiloMixin, forms.ModelForm):
    username = forms.CharField(label="Username", required=True)
    nome = forms.CharField(max_length=50, label="Nome", required=True, widget=forms.TextInput(attrs={'placeholder': 'Es. Mario'}))
    cognome = forms.CharField(max_length=50, label="Cognome", required=True, widget=forms.TextInput(attrs={'placeholder': 'Es. Rossi'}))
    email = forms.EmailField(label="Email", required=True)
    
    foto_profilo = forms.ImageField(
        required=False, 
        label="Foto Profilo", 
        widget=forms.FileInput()
    )

    class Meta:
        model = Profilo
        fields = ['ruolo', 'eta', 'citta', 'foto_profilo']
        widgets = {
            'eta': forms.NumberInput(attrs={'min': '18', 'max': '100'}),
            'citta': forms.TextInput(attrs={'placeholder': 'Es. Roma'})
        }

    field_order = ['username', 'ruolo', 'nome', 'cognome', 'email', 'eta', 'citta', 'foto_profilo', 'elimina_foto']

    def __init__(self, *args, **kwargs):
        user = kwargs['instance'].user
        super().__init__(*args, **kwargs)
        
        self.fields['username'].initial = user.username
        self.fields['nome'].initial = user.first_name
        self.fields['cognome'].initial = user.last_name
        self.fields['email'].initial = user.email
        self.fields['ruolo'].disabled = True

        if self.instance and self.instance.foto_profilo:
            self.fields['elimina_foto'] = forms.BooleanField(
                required=False, 
                label="Rimuovi foto attuale"
            )

    def clean_username(self):
        """Questa rimane qui perché è specifica solo della modifica"""
        nuovo_username = self.cleaned_data.get('username')
        user_corrente = self.instance.user
        
        if nuovo_username and nuovo_username != user_corrente.username:
            if User.objects.filter(username=nuovo_username).exists():
                raise forms.ValidationError("Questo username è già in uso. Scegline un altro.")
        return nuovo_username

    def save(self, commit=True):
        profilo = super().save(commit=False)
        user = profilo.user
        vecchio_username = user.username
        
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['nome']
        user.last_name = self.cleaned_data['cognome']
        user.email = self.cleaned_data['email']
        user.save()

        if vecchio_username != user.username and profilo.foto_profilo:
            estensione = os.path.splitext(profilo.foto_profilo.name)[1]
            nuovo_nome_file = f"foto_profilo/{user.username}{estensione}"
            
            vecchio_path = profilo.foto_profilo.path
            nuovo_path = os.path.join(settings.MEDIA_ROOT, nuovo_nome_file)
            
            os.rename(vecchio_path, nuovo_path)
            
            profilo.foto_profilo.name = nuovo_nome_file

        if self.cleaned_data.get('elimina_foto'):
            profilo.foto_profilo.delete(save=False)
            profilo.foto_profilo = None            
        
        if commit:
            profilo.save()
            
        return profilo
    
class RecensioneForm(forms.ModelForm):
    class Meta:
        model = Recensione
        fields = ['voto', 'testo']
        widgets = {
            'voto': forms.Select(attrs={
                'style': 'width: 100%; padding: 15px; border-radius: 15px; border: 1px solid #fde4d0; background: #fff8f3; font-size: 16px; font-weight: 700; color: #ef6c00; margin-bottom: 20px;'
            }),
            'testo': forms.Textarea(attrs={
                'style': 'width: 100%; padding: 15px; border-radius: 15px; border: 1px solid #ccc; font-size: 14px; margin-bottom: 20px; font-family: inherit;',
                'rows': 4,
                'placeholder': 'Racconta la tua esperienza (es. Spedizione veloce, strumento in ottime condizioni...)'
            }),
        }
        labels = {
            'voto': 'Voto (da 1 a 5 Stelle)',
            'testo': 'La tua recensione'
        }