import os
from django.db import models
from django.contrib.auth.models import User

def path_foto_profilo(instance, filename):
    ext = filename.split('.')[-1]
    nome_file = f"{instance.user.username}.{ext}"
    return os.path.join('foto_profilo', nome_file)

class Profilo(models.Model):
    RUOLI_SCELTA = (
        ('acquirente', 'Acquirente'),
        ('venditore', 'Venditore'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    eta = models.IntegerField(null=True, blank=True)
    citta = models.CharField(max_length=100, null=True, blank=True)
    ruolo = models.CharField(max_length=20, choices=RUOLI_SCELTA, default='acquirente')

    foto_profilo = models.ImageField(upload_to=path_foto_profilo, null=True, blank=True)

    def __str__(self):
        return f"Profilo di {self.user.username} ({self.ruolo})"

    @property
    def foto_profilo_url(self):
        if self.foto_profilo and hasattr(self.foto_profilo, 'url'):
            return self.foto_profilo.url
        return '/static/img/avatar.svg'