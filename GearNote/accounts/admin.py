from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profilo

# Definiamo un "inline" che mostra il profilo dentro la pagina dell'utente
class ProfiloInline(admin.StackedInline):
    model = Profilo
    can_delete = False
    verbose_name_plural = 'Profilo'

# Re-registriamo l'utente includendo il profilo
class UserAdmin(BaseUserAdmin):
    inlines = (ProfiloInline,)

# Rimuoviamo la registrazione standard e usiamo quella personalizzata
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

def create_superuser(sender, **kwargs):
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@gear.note', 'admin')
        print("Superuser 'admin' creato con successo.")