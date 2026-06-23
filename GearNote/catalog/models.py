import os
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    
    # LA NUOVA LOGICA: Categorie Padre/Figlio
    categoria_padre = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='sottocategorie'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome) # Crea lo slug automaticamente dal nome
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categorie"

    def __str__(self):
        if self.categoria_padre:
            return f"{self.categoria_padre.nome} -> {self.nome}"
        return self.nome
    
    @property
    def ha_prodotti_attivi(self):
        """Proprietà ricorsiva: vera se la categoria o i suoi discendenti hanno prodotti in vendita"""
        # 1. Controlla se ci sono prodotti direttamente in questa categoria
        if self.prodotti.filter(disponibile=True).exists():
            return True
        # 2. Se non ci sono, chiede alle sue sottocategorie (ricorsione)
        for figlio in self.sottocategorie.all():
            if figlio.ha_prodotti_attivi:
                return True
        return False

# --- IL NUOVO MODELLO CONDIZIONE (Sostituisce il Tag) ---
class Condizione(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Condizioni"

    def __str__(self):
        return self.nome

class Prodotto(models.Model):
    venditore = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prodotti_in_vendita')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='prodotti')
    
    # --- LA NUOVA CHIAVE ESTERNA PER LA CONDIZIONE ---
    condizione = models.ForeignKey(Condizione, on_delete=models.PROTECT, related_name='prodotti')
    
    titolo = models.CharField(max_length=200)
    descrizione = models.TextField()
    
    # VALIDAZIONE AL DATABASE: Impedisce prezzi negativi o pari a zero
    prezzo = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    disponibile = models.BooleanField(default=True, help_text="Togli la spunta se l'oggetto è stato venduto")
    data_inserimento = models.DateTimeField(auto_now_add=True)
    data_modifica = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_inserimento']

    def __str__(self):
        return f"{self.titolo} - {self.prezzo}€"

    @property
    def immagine_principale(self):
        # 1. Cerca l'immagine marcata come principale
        prima_foto = self.immagini.filter(principale=True).first()
        if prima_foto:
            return prima_foto.immagine.url
        
        # 2. Logica per le icone di default basata sulla macro-categoria
        # Risaliamo alla radice (macro-categoria)
        cat_radice = self.categoria
        while cat_radice and cat_radice.categoria_padre:
            cat_radice = cat_radice.categoria_padre
            
        # Se la macro-categoria è "Partiture" (aggiusta il nome o l'ID come preferisci)
        if cat_radice and "partiture" in cat_radice.nome.lower():
            return '/static/img/spartito.svg'
        
        # Default per Strumenti e tutto il resto
        return '/static/img/prodotto.svg'

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