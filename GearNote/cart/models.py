from django.db import models
from django.contrib.auth.models import User
from catalog.models import Prodotto 

class Carrello(models.Model):
    utente = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrello')
    creato_il = models.DateTimeField(auto_now_add=True)
    aggiornato_il = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carrello di {self.utente.username}"

    @property
    def totale_carrello(self):
        elementi = self.elementi.all()
        return sum([elemento.totale for elemento in elementi])

    @property
    def numero_articoli(self):
        elementi = self.elementi.all()
        return sum([elemento.quantita for elemento in elementi])

class ElementoCarrello(models.Model):
    carrello = models.ForeignKey(Carrello, on_delete=models.CASCADE, related_name='elementi')
    prodotto = models.ForeignKey(Prodotto, on_delete=models.CASCADE)
    quantita = models.PositiveIntegerField(default=1)
    aggiunto_il = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('carrello', 'prodotto')

    def __str__(self):
        return f"{self.quantita} x {self.prodotto.titolo}"

    @property
    def totale(self):
        return self.prodotto.prezzo * self.quantita
    
class Ordine(models.Model):
    utente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ordini')
    nome_completo = models.CharField(max_length=100)
    indirizzo = models.CharField(max_length=250)
    citta = models.CharField(max_length=100)
    cap = models.CharField(max_length=10)
    totale = models.DecimalField(max_digits=10, decimal_places=2)
    creato_il = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ordine #{self.id} - {self.utente.username}"

class ElementoOrdine(models.Model):
    ordine = models.ForeignKey(Ordine, on_delete=models.CASCADE, related_name='elementi')
    prodotto = models.ForeignKey('catalog.Prodotto', on_delete=models.SET_NULL, null=True) 
    prezzo_pagato = models.DecimalField(max_digits=10, decimal_places=2) 

    def __str__(self):
        titolo = self.prodotto.titolo if self.prodotto else "Prodotto rimosso"
        return f"{titolo} - Ordine #{self.ordine.id}"