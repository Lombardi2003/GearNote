from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profilo

class RegistrazioneForm(UserCreationForm):
    # Aggiungiamo il menu a tendina per far scegliere il ruolo all'utente
    ruolo = forms.ChoiceField(
        choices=Profilo.RUOLI_CHOICES, 
        required=True, 
        label="Cosa vuoi fare su UniSound?"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Oltre a username e password (già gestiti in automatico), aggiungiamo l'email
        fields = UserCreationForm.Meta.fields + ('email',)