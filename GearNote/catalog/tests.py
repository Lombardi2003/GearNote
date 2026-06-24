from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from catalog.models import Prodotto, Condizione # Aggiunto l'import per Condizione
from accounts.models import Profilo 

class SicurezzaCatalogoTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # 1. Creiamo i Venditori e l'Acquirente (Stesso codice di prima)
        self.venditore_vittima = User.objects.create_user(username='venditore_vero', password='password123')
        profilo_vittima, _ = Profilo.objects.get_or_create(user=self.venditore_vittima)
        profilo_vittima.ruolo = 'venditore'
        profilo_vittima.save()

        self.venditore_hacker = User.objects.create_user(username='venditore_fake', password='password123')
        profilo_hacker, _ = Profilo.objects.get_or_create(user=self.venditore_hacker)
        profilo_hacker.ruolo = 'venditore'
        profilo_hacker.save()

        self.acquirente = User.objects.create_user(username='acquirente', password='password123')
        profilo_acq, _ = Profilo.objects.get_or_create(user=self.acquirente)
        profilo_acq.ruolo = 'acquirente'
        profilo_acq.save()

        # 🌟 2. CREIAMO LA CONDIZIONE OBBLIGATORIA
        # Presumo che il tuo modello Condizione abbia un campo 'nome' (es: Nuovo, Usato)
        # Se il campo si chiama in modo diverso (es. 'descrizione'), modificalo qui sotto.
        self.condizione_usato = Condizione.objects.create(nome='Usato')

        # 3. Creiamo il prodotto assegnando la condizione!
        self.prodotto = Prodotto.objects.create(
            titolo='Fender Stratocaster Originale',
            descrizione='Suona da dio',
            prezzo=1500.00,
            venditore=self.venditore_vittima,
            condizione=self.condizione_usato, # <-- ECCO IL PEZZO MANCANTE
            disponibile=True
            # NOTA: Se hai anche una Categoria obbligatoria come ForeignKey,
            # dovrai importare e creare anche quella allo stesso modo.
        )

    def test_acquirente_bloccato_da_creazione(self):
        self.client.login(username='acquirente', password='password123')
        response = self.client.get(reverse('catalog:aggiungi_prodotto'))
        self.assertNotEqual(response.status_code, 200, "ERRORE: Un acquirente riesce a vedere il form di vendita!")

    def test_venditore_non_puo_modificare_altri(self):
        self.client.login(username='venditore_fake', password='password123')
        url_modifica = reverse('catalog:modifica_prodotto', args=[self.prodotto.id])
        self.client.post(url_modifica, {
            'titolo': 'Fender Stratocaster Originale',
            'descrizione': 'Hackerato!',
            'prezzo': 1.00,
            'condizione': self.condizione_usato.id # Dobbiamo passarlo anche nella finta form POST
        })
        self.prodotto.refresh_from_db()
        self.assertEqual(float(self.prodotto.prezzo), 1500.00, "FALLA: L'hacker ha modificato il prezzo di un altro venditore!")

    def test_venditore_non_puo_eliminare_altri(self):
        self.client.login(username='venditore_fake', password='password123')
        url_elimina = reverse('catalog:elimina_prodotto', args=[self.prodotto.id])
        self.client.post(url_elimina)
        prodotto_esiste = Prodotto.objects.filter(id=self.prodotto.id).exists()
        self.assertTrue(prodotto_esiste, "FALLA: L'hacker ha eliminato il prodotto di un altro venditore!")