from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

from .views import CustomLoginView

app_name = 'accounts'

urlpatterns = [
    path('registrati/', views.registrazione_view, name='registrati'),
    
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profilo/', views.profilo_view, name='profilo'),

    path('modifica/', views.modifica_profilo, name='modifica_profilo'),

    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/cambia_password.html',
        success_url='/accounts/profilo/'
    ), name='password_change'),
]