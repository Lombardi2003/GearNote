from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

from .views import CustomLoginView

app_name = 'accounts'

urlpatterns = [
    path('registrati/', views.registrazione_view, name='registrati'),
    path('login/', CustomLoginView.as_view(), name='login'),
    # Django 5 richiede una richiesta POST per il logout nativo, che gestiremo tramite form
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Nuova rotta per la dashboard dell'utente
    path('profilo/', views.profilo_view, name='profilo'),
]