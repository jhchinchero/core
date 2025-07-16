#libros/views.py
from django.shortcuts import render
from core.models import Libro

from django.contrib import messages
from django.utils import timezone




def lista_libros(request):
    libros = Libro.objects.prefetch_related('autores', 'ejemplares', 'editorial')
    return render(request, 'listado.html', {'libros': libros})