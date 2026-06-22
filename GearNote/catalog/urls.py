from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.lista_prodotti, name='lista'),
    path('prodotto/<int:id>/', views.dettaglio_prodotto, name='dettaglio')
]