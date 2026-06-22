from django.apps import AppConfig
from django.db.models.signals import post_migrate

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Colleghiamo la funzione di setup al segnale post_migrate
        post_migrate.connect(setup_system, sender=self)

def setup_system(sender, **kwargs):
    from django.contrib.auth.models import Group, User
    
    # 1. Creazione Gruppi
    groups = ['Venditore', 'Acquirente']
    for group_name in groups:
        Group.objects.get_or_create(name=group_name)
    print("--- Gruppi verificati/creati ---")

    # 2. Creazione Superuser Admin
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@gear.note', 'admin')
        print("--- Superuser 'admin' creato ---")