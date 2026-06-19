from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Profilo

# --- FORM DI REGISTRAZIONE (Intatto) ---
class RegistrazionePersonalizzataForm(UserCreationForm):
    nome = forms.CharField(max_length=50, label="Nome")
    cognome = forms.CharField(max_length=50, label="Cognome")
    email = forms.EmailField(label="Email")
    eta = forms.IntegerField(label="Età")
    citta = forms.CharField(max_length=100, label="Città")
    
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


# --- FORM DI MODIFICA (Ottimizzato per il tuo HTML) ---
class ModificaProfiloForm(forms.ModelForm):
    # 1. SBLOCCATO L'USERNAME (rimosso disabled=True)
    username = forms.CharField(label="Username", required=True)
    nome = forms.CharField(max_length=50, label="Nome", required=True)
    cognome = forms.CharField(max_length=50, label="Cognome", required=True)
    email = forms.EmailField(label="Email", required=True)
    
    foto_profilo = forms.ImageField(
        required=False, 
        label="Foto Profilo", 
        widget=forms.FileInput()
    )

    class Meta:
        model = Profilo
        fields = ['ruolo', 'eta', 'citta', 'foto_profilo']

    # Abbiamo aggiunto 'elimina_foto' alla fine della lista
    field_order = ['username', 'ruolo', 'nome', 'cognome', 'email', 'eta', 'citta', 'foto_profilo', 'elimina_foto']

    def __init__(self, *args, **kwargs):
        user = kwargs['instance'].user
        super().__init__(*args, **kwargs)
        
        self.fields['username'].initial = user.username
        self.fields['nome'].initial = user.first_name
        self.fields['cognome'].initial = user.last_name
        self.fields['email'].initial = user.email
        self.fields['ruolo'].disabled = True

        # 2. SE L'UTENTE HA UNA FOTO, CREIAMO IL PULSANTINO "ELIMINA"
        if self.instance and self.instance.foto_profilo:
            self.fields['elimina_foto'] = forms.BooleanField(
                required=False, 
                label="Rimuovi foto attuale"
            )

    # 3. CONTROLLO USERNAME DOPPIO
    def clean_username(self):
        nuovo_username = self.cleaned_data.get('username')
        user_corrente = self.instance.user
        
        # Se ha cambiato username, controlliamo se il nuovo esiste già
        if nuovo_username and nuovo_username != user_corrente.username:
            if User.objects.filter(username=nuovo_username).exists():
                raise forms.ValidationError("Questo username è già in uso. Scegline un altro.")
        return nuovo_username

    def save(self, commit=True):
        profilo = super().save(commit=False)
        user = profilo.user
        
        # Salviamo il nuovo username
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['nome']
        user.last_name = self.cleaned_data['cognome']
        user.email = self.cleaned_data['email']

        # 4. GESTIONE ELIMINAZIONE FOTO
        if self.cleaned_data.get('elimina_foto'):
            profilo.foto_profilo.delete(save=False) # Cancella il file fisico
            profilo.foto_profilo = None             # Svuota il database
        
        if commit:
            user.save()
            profilo.save()
            
        return profilo