from django import forms
from .models import Prodotto

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={'multiple': True, 'class': 'form-control'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ProdottoForm(forms.ModelForm):
    foto = MultipleFileField(
        required=False,
        label="Carica le foto dello strumento"
    )

    class Meta:
        model = Prodotto
        fields = [
            'titolo', 
            'categoria', 
            'condizione', 
            'prezzo', 
            'descrizione'
        ]
        
        widgets = {
            'titolo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Es. Fender Stratocaster Americana...'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'condizione': forms.Select(attrs={'class': 'form-select'}),
            'prezzo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descrizione': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descrivi eventuali difetti, anno di produzione, accessori inclusi...'}),
        }

    # VALIDAZIONE PREZZO (Lato Utente per feedback visivo rapido)
    def clean_prezzo(self):
        prezzo = self.cleaned_data.get('prezzo')
        if prezzo is not None and prezzo <= 0:
            raise forms.ValidationError("Il prezzo deve essere maggiore di zero.")
        return prezzo

    # VALIDAZIONE TITOLO
    def clean_titolo(self):
        titolo = self.cleaned_data.get('titolo')
        if len(titolo) < 5:
            raise forms.ValidationError("Il titolo è troppo breve, inserisci almeno 5 caratteri.")
        return titolo

    # VALIDAZIONE DESCRIZIONE
    def clean_descrizione(self):
        descrizione = self.cleaned_data.get('descrizione')
        if len(descrizione) < 20:
            raise forms.ValidationError("La descrizione deve contenere almeno 20 caratteri per aiutare la vendita.")
        return descrizione

    # VALIDAZIONE FOTO (Controllo sul peso del file)
    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if foto:
            for f in foto:
                if f.size > 5 * 1024 * 1024:  # Limite 5MB
                    raise forms.ValidationError(f"Il file {f.name} è troppo grande (max 5MB).")
        return foto