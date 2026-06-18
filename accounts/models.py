from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profilo(models.Model):
    RUOLI_CHOICES = [
        ('ACQUIRENTE', 'Utente Registrato - Acquirente'),
        ('VENDITORE', 'Utente Registrato - Venditore'),
    ]
    
    # Collega il profilo direttamente all'utente base di Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profilo')
    eta = models.PositiveIntegerField(null=True, blank=True)
    citta = models.CharField(max_length=100, null=True, blank=True)
    ruolo = models.CharField(max_length=20, choices=RUOLI_CHOICES, default='ACQUIRENTE')

    def __str__(self):
        return f"Profilo di {self.user.username} ({self.get_ruolo_display()})"

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