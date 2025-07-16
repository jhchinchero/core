from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.hashers import make_password

import uuid
import os

def libro_foto_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('libros/', filename)


class Editorial(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nombre


class Autor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    anio = models.PositiveIntegerField(verbose_name='Año')
    isbn = models.CharField(max_length=20, unique=True, verbose_name='Identificador único para libros')
    foto = models.ImageField(upload_to=libro_foto_upload_path, blank=True, null=True)
    editorial = models.ForeignKey(Editorial, on_delete=models.CASCADE, related_name='libros')
    autores = models.ManyToManyField(Autor, related_name='libros')

    def __str__(self):
        return f"{self.titulo} ({self.anio})"


class Ejemplar(models.Model):
    ESTADOS = [
        ('nuevo', 'Nuevo'),
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('malo', 'Malo'),
    ]

    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='ejemplares')
    codigo = models.CharField(max_length=50)
    estado = models.CharField(max_length=10, choices=ESTADOS)

    def __str__(self):
        return f"{self.libro.titulo} - {self.codigo}"



class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    TIPOS = [
        ('estudiante', 'Estudiante'),
        ('docente', 'Docente'),
        ('administrativo', 'Administrativo'),
    ]

    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    tipo = models.CharField(max_length=20, choices=TIPOS)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido', 'telefono', 'tipo']

    def __str__(self):
        return f'{self.nombre} {self.apellido} ({self.email})'

class Prestamo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='prestamos')
    ejemplar = models.ForeignKey(Ejemplar, on_delete=models.CASCADE, related_name='prestamos')
    fecha_prestamo = models.DateField()
    fecha_devolucion = models.DateField()
    devuelto = models.BooleanField(default=False)  # ← Nuevo campo

    def __str__(self):
        estado = "Devuelto" if self.devuelto else "Prestado"
        return f"{self.usuario} → {self.ejemplar} ({estado})"





class Reserva(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='reservas')
    fecha_reserva = models.DateField()
    atendida = models.BooleanField(default=False)  # Nuevo campo opcional

    def __str__(self):
        estado = "Atendida" if self.atendida else "Pendiente"
        return f"{self.usuario} reservó {self.libro} ({estado})"