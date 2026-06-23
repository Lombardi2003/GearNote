from django import forms
from .models import Prodotto

# 1. Il widget che abilita la selezione multipla nel browser
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

# 2. LA SOLUZIONE LOGICA: Un campo form personalizzato che sa convalidare una LISTA di file
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={'multiple': True, 'class': 'form-control'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            # Se riceviamo una lista di file, li convalidiamo uno per uno
            result = [single_file_clean(d, initial) for d in data]
        else:
            # Se è un file singolo, usiamo la convalida standard
            result = single_file_clean(data, initial)
        return result


# 3. IL TUO FORM AGGIORNATO
class ProdottoForm(forms.ModelForm):
    # Sostituiamo forms.FileField con il nostro nuovo MultipleFileField
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