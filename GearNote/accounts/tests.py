from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Profilo

class AccountsSicurezzaTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.utente_test = User.objects.create_user(username='musicista_pro', password='password_sicura123')
        self.profilo_test = Profilo.objects.create(user=self.utente_test, ruolo='venditore')

    def test_protezione_dashboard_anonimo(self):
        """Redirect preciso: anonimo → login, non solo 'non 200'."""
        response = self.client.get(reverse('accounts:profilo'))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:profilo')}",
            msg_prefix="Un utente anonimo non viene rimandato al login corretto"
        )

    def test_accesso_dashboard_utente_loggato(self):
        """L'utente vede la SUA dashboard, non quella di chiunque."""
        self.client.login(username='musicista_pro', password='password_sicura123')
        response = self.client.get(reverse('accounts:profilo'))
        self.assertEqual(response.status_code, 200)
        # Verifica che il contesto contenga i dati dell'utente corretto
        self.assertEqual(response.context['user'], self.utente_test)

    def test_cascade_delete_profilo(self):
        """Eliminando l'User, il Profilo collegato deve sparire (CASCADE)."""
        profilo_id = self.profilo_test.id
        self.utente_test.delete()
        self.assertFalse(
            Profilo.objects.filter(id=profilo_id).exists(),
            "BUG: Il Profilo è rimasto orfano dopo la cancellazione dell'User!"
        )

    def test_cambio_password_invalida_sessione(self):
        """Dopo un cambio password, la vecchia sessione non deve essere più valida."""
        self.client.login(username='musicista_pro', password='password_sicura123')
        # Cambia la password
        self.utente_test.set_password('nuova_password_456')
        self.utente_test.save()
        # La vecchia sessione non deve più funzionare
        response = self.client.get(reverse('accounts:profilo'))
        self.assertNotEqual(
            response.status_code, 200,
            "FALLA DI SICUREZZA: Una sessione rimane valida dopo il cambio password!"
        )