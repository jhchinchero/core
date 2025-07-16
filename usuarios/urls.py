# usuarios/urls.py
from django.urls import path
from .views import registro_view, login_view, logout_view, perfil_view

app_name = 'usuarios'

urlpatterns = [
    path('register/', registro_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('perfil/', perfil_view, name='perfil'),
]
