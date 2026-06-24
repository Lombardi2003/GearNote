from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from catalog.models import Prodotto, Condizione
from accounts.models import Profilo
from cart.models import Carrello, ElementoCarrello

class CarrelloEstremoTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # 1. Setup Utenti
        self.acquirente = User.objects.create_user(username='acquirente_serio', password='password123')
        Profilo.objects.create(user=self.acquirente, ruolo='acquirente')
        
        self.venditore = User.objects.create_user(username='venditore_negozio', password='password123')
        Profilo.objects.create(user=self.venditore, ruolo='venditore')
        
        # 2. Setup Condizione (Obbligatoria come visto prima)
        self.condizione = Condizione.objects.create(nome='Ottimo Stato')
        
        # 3. Prodotto Normale
        self.prodotto_disponibile = Prodotto.objects.create(
            titolo='Fender Jazz Bass',
            descrizione='Perfetto per slap',
            prezzo=1000.00,
            venditore=self.venditore,
            condizione=self.condizione,
            disponibile=True
        )
        
        # 4. Prodotto Già Venduto
        self.prodotto_venduto = Prodotto.objects.create(
            titolo='Gibson Les Paul Storica',
            descrizione='Pezzo da collezione, appena venduto',
            prezzo=2500.00,
            venditore=self.venditore,
            condizione=self.condizione,
            disponibile=False
        )

    def test_doppia_aggiunta_stesso_prodotto_unico(self):
        """TEST NON BANALE 1: Previene la clonazione dei pezzi unici."""
        self.client.login(username='acquirente_serio', password='password123')
        
        url = reverse('cart:aggiungi_al_carrello')
        # L'utente aggiunge il basso la prima volta
        self.client.post(url, {'prodotto_id': self.prodotto_disponibile.id})
        
        # L'utente ricarica la pagina o usa uno script per forzare una seconda aggiunta
        self.client.post(url, {'prodotto_id': self.prodotto_disponibile.id})
        
        # Recuperiamo il suo elemento dal carrello
        carrello = Carrello.objects.get(utente=self.acquirente)
        elemento = ElementoCarrello.objects.get(carrello=carrello, prodotto=self.prodotto_disponibile)
        
        # Essendo roba usata, la quantità NON DEVE superare 1. 
        self.assertEqual(elemento.quantita, 1, "BUG LOGICO: Il carrello ha permesso di impostare quantità=2 per un pezzo unico usato!")

    def test_aggiunta_prodotto_gia_venduto(self):
            """TEST NON BANALE 2: Previene l'aggiunta di prodotti non disponibili."""
            self.client.login(username='acquirente_serio', password='password123')
            
            url = reverse('cart:aggiungi_al_carrello')
            # L'utente forza l'ID della Gibson che ha disponibile=False
            self.client.post(url, {'prodotto_id': self.prodotto_venduto.id})
            
            # Visto che la nostra sicurezza blocca l'utente prima ancora di creare il carrello,
            # usiamo un filtro diretto e sicuro per contare se l'elemento è stato aggiunto,
            # navigando attraverso la relazione (carrello__utente).
            elementi_nel_carrello = ElementoCarrello.objects.filter(
                carrello__utente=self.acquirente, 
                prodotto=self.prodotto_venduto
            ).count()
            
            self.assertEqual(elementi_nel_carrello, 0, "VULNERABILITÀ: Il sistema permette di mettere in carrello prodotti non disponibili!")

    def test_venditore_prova_ad_usare_carrello(self):
        """TEST NON BANALE 3: Controllo ruoli sul carrello."""
        self.client.login(username='venditore_negozio', password='password123')
        
        url = reverse('cart:aggiungi_al_carrello')
        # Il venditore prova a interagire con la rotta di acquisto
        self.client.post(url, {'prodotto_id': self.prodotto_disponibile.id})
        
        # Assicuriamoci che non sia stato creato nessun elemento carrello in assoluto
        elementi_totali = ElementoCarrello.objects.filter(prodotto=self.prodotto_disponibile).count()
        
        self.assertEqual(elementi_totali, 0, "VULNERABILITÀ RUOLI: Un venditore è riuscito a infilare roba nel sistema carrelli!")