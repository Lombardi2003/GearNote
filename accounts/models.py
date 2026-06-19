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

# Questi segnali creano automaticamente un Profilo vuoto ogni volta che un nuovo User si registra
# Il primo segnale rimane invariato
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profilo.objects.create(user=instance)

# Aggiungiamo un controllo di sicurezza al secondo segnale
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Salva il profilo SOLO se l'utente ne possiede effettivamente uno
    if hasattr(instance, 'profilo'):
        instance.profilo.save()