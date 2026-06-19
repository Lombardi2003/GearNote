from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profilo(models.Model):
    # Creiamo le scelte disponibili (Il primo valore va nel DB, il secondo lo legge l'utente)
    RUOLI_SCELTA = (
        ('acquirente', 'Acquirente'),
        ('venditore', 'Venditore'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    eta = models.IntegerField(null=True, blank=True)
    citta = models.CharField(max_length=100, null=True, blank=True)
    
    # Aggiungiamo il campo ruolo. Impostiamo Acquirente come default per sicurezza.
    ruolo = models.CharField(max_length=20, choices=RUOLI_SCELTA, default='acquirente')

    # Foto del profilo (opzionale)
    foto_profilo = models.ImageField(upload_to='foto_profilo/', null=True, blank=True)

    def __str__(self):
        return f"Profilo di {self.user.username} ({self.ruolo})"

    @property
    def foto_profilo_url(self):
        if self.foto_profilo and hasattr(self.foto_profilo, 'url'):
            return self.foto_profilo.url
        else:
            # Qui punta esattamente al file che hai appena salvato
            return '/static/img/avatar.svg'