#libros/urls.py
from django.urls import path
from . import views

app_name = 'libros'

urlpatterns = [
    path('libros', views.lista_libros, name='listado'),
  
]
