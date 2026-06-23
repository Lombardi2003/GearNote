from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.lista_prodotti, name='lista'),
    path('prodotto/<int:id>/', views.dettaglio_prodotto, name='dettaglio'),
    path('nuovo-annuncio/', views.aggiungi_prodotto, name='aggiungi_prodotto'),
    path('prodotto/<int:prodotto_id>/modifica/', views.modifica_prodotto, name='modifica_prodotto'),
    path('prodotto/<int:prodotto_id>/elimina/', views.elimina_prodotto, name='elimina_prodotto'),
]