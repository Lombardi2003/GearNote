import os
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    
    categoria_padre = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='sottocategorie'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
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
        if self.prodotti.filter(disponibile=True).exists():
            return True
        for figlio in self.sottocategorie.all():
            if figlio.ha_prodotti_attivi:
                return True
        return False

class Condizione(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Condizioni"

    def __str__(self):
        return self.nome

class Prodotto(models.Model):
    venditore = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prodotti_in_vendita')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='prodotti')
    
    condizione = models.ForeignKey(Condizione, on_delete=models.PROTECT, related_name='prodotti')
    
    titolo = models.CharField(max_length=200)
    descrizione = models.TextField()
    
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
        prima_foto = self.immagini.filter(principale=True).first()
        if prima_foto:
            return prima_foto.immagine.url
        

        cat_radice = self.categoria
        while cat_radice and cat_radice.categoria_padre:
            cat_radice = cat_radice.categoria_padre
            
        if cat_radice and "partiture" in cat_radice.nome.lower():
            return '/static/img/spartito.svg'
        
        return '/static/img/prodotto.svg'

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