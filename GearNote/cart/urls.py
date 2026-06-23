from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.vedi_carrello, name='vedi_carrello'),
    path('aggiungi/', views.aggiungi_al_carrello, name='aggiungi_al_carrello'),
    path('rimuovi/', views.rimuovi_dal_carrello, name='rimuovi_dal_carrello'),
    path('checkout/', views.checkout, name='checkout')
]