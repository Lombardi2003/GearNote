import os
from django.db import models
from django.contrib.auth.models import User

# --- FUNZIONE PER RINOMINARE IL FILE ---
def path_foto_profilo(instance, filename):
    # Otteniamo l'estensione del file originale (es: .jpg, .png)
    ext = filename.split('.')[-1]
    # Creiamo il nuovo nome basato sullo username dell'utente
    nome_file = f"{instance.user.username}.{ext}"
    # Il file verrà salvato in 'media/foto_profilo/username.jpg'
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

    # --- MODIFICA QUI: usiamo la funzione appena creata ---
    foto_profilo = models.ImageField(upload_to=path_foto_profilo, null=True, blank=True)

    def __str__(self):
        return f"Profilo di {self.user.username} ({self.ruolo})"

    @property
    def foto_profilo_url(self):
        if self.foto_profilo and hasattr(self.foto_profilo, 'url'):
            return self.foto_profilo.url
        return '/static/img/avatar.svg'