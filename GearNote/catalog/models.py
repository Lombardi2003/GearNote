from django.db import models
from django.contrib.auth.models import User
import os

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, help_text="Versione URL del nome (es. 'chitarre-elettriche')")
    
    # LA NUOVA LOGICA: Categorie Padre/Figlio
    categoria_padre = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='sottocategorie'
    )

    class Meta:
        verbose_name_plural = "Categorie"

    def __str__(self):
        if self.categoria_padre:
            return f"{self.categoria_padre.nome} -> {self.nome}"
        return self.nome

# --- IL NUOVO MODELLO TAG ---
class Tag(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome

class Prodotto(models.Model):
    CONDIZIONE_SCELTE = [
        ('nuovo', 'Nuovo'),
        ('usato_ottimo', 'Usato - Come Nuovo'),
        ('usato_buono', 'Usato - Buone Condizioni'),
        ('usato_accettabile', 'Usato - Accettabile'),
        ('da_riparare', 'Non Funzionante / Da Riparare'),
    ]
    
    STRUMENTI_SCELTE = [
        ('sax', 'Sassofono'),
        ('chitarra_el', 'Chitarra Elettrica'),
        ('chitarra_ac', 'Chitarra Acustica'),
        ('basso', 'Basso Elettrico'),
        ('piano', 'Pianoforte e Tastiere'),
        ('batteria', 'Batteria e Percussioni'),
        ('fiati_altri', 'Altri Fiati (Tromba, Flauto, ecc.)'),
        ('universale', 'Universale / Non specifico'),
    ]

    venditore = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prodotti_in_vendita')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='prodotti')
    
    # --- COLLEGAMENTO DEL TAG AL PRODOTTO ---
    tag = models.ManyToManyField(Tag, blank=True)
    
    strumento_riferimento = models.CharField(
        max_length=50, 
        choices=STRUMENTI_SCELTE,
        help_text="Seleziona lo strumento a cui è destinato questo prodotto. Scegli 'Universale' se va bene per tutti."
    )
    
    titolo = models.CharField(max_length=200)
    descrizione = models.TextField()
    prezzo = models.DecimalField(max_digits=10, decimal_places=2)
    condizione = models.CharField(max_length=20, choices=CONDIZIONE_SCELTE, default='usato_buono')
    
    disponibile = models.BooleanField(default=True, help_text="Togli la spunta se l'oggetto è stato venduto")
    data_inserimento = models.DateTimeField(auto_now_add=True)
    data_modifica = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_inserimento']

    def __str__(self):
        return f"{self.titolo} - {self.prezzo}€"


# --- GESTIONE FOTO PRODOTTI ---
def path_foto_prodotto(instance, filename):
    prodotto_id = instance.prodotto.id if instance.prodotto.id else 'nuovi'
    return os.path.join('prodotti', str(prodotto_id), filename)

class ImmagineProdotto(models.Model):
    prodotto = models.ForeignKey(Prodotto, on_delete=models.CASCADE, related_name='immagini')
    immagine = models.ImageField(upload_to=path_foto_prodotto)
    principale = models.BooleanField(default=False, help_text="Usa come foto copertina")

    class Meta:
        verbose_name_plural = "Immagini Prodotti"

    def __str__(self):
        return f"Immagine per {self.prodotto.titolo}"