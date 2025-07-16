from django.contrib import admin
from .models import Editorial, Autor, Libro, Ejemplar, Usuario, Prestamo, Reserva
from django.contrib import messages
from django.utils import timezone


# Inline para añadir ejemplares directamente desde Libro
class EjemplarInline(admin.TabularInline):
    model = Ejemplar
    extra = 1


@admin.register(Editorial)
class EditorialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono')
    search_fields = ('nombre',)


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido')
    search_fields = ('nombre', 'apellido')

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'anio', 'isbn', 'editorial')
    list_filter = ('anio', 'editorial')
    search_fields = ('titulo', 'isbn')
    autocomplete_fields = ('editorial', 'autores')
    inlines = [EjemplarInline]


    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'anio', 'isbn', 'foto')
        }),
        ('Editorial y autores', {
            'fields': ('editorial', 'autores'),
        }),
    )
    def mostrar_anio(self, obj):
        return obj.anio
    mostrar_anio.short_description = 'Año'
    def mostrar_isbn(self, obj):
        return obj.isbn
    mostrar_isbn.short_description = 'Identificador único para libros'
    def cantidad_ejemplares(self, obj):
        return obj.ejemplares.count()
    cantidad_ejemplares.short_description = 'Ejemplares'



@admin.register(Ejemplar)
class EjemplarAdmin(admin.ModelAdmin):
    list_display = ('libro', 'codigo', 'estado')
    list_filter = ('estado',)
    search_fields = ('codigo',)
    autocomplete_fields = ('libro',)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'tipo')
    list_filter = ('tipo',)
    search_fields = ('nombre', 'apellido', 'email')





@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'ejemplar', 'fecha_prestamo', 'fecha_devolucion', 'devuelto')  # ← incluye aquí 'devuelto'
    list_filter = ('fecha_prestamo', 'fecha_devolucion', 'devuelto')
    list_editable = ('devuelto',)  # ← ahora sí es válido
    autocomplete_fields = ('usuario', 'ejemplar')

    def save_model(self, request, obj, form, change):
        # Verificar si el ejemplar ya tiene un préstamo activo
        prestamos_activos = Prestamo.objects.filter(
            ejemplar=obj.ejemplar,
            fecha_devolucion__gte=timezone.now().date(),
            devuelto=False

        )
        # Si es edición, excluir el propio objeto
        if change:
            prestamos_activos = prestamos_activos.exclude(pk=obj.pk)

        if prestamos_activos.exists():
            self.message_user(request,
                "Error: Este ejemplar ya está prestado y no ha sido devuelto.",
                level=messages.ERROR
            )
        else:
            super().save_model(request, obj, form, change)




@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'libro', 'fecha_reserva', 'atendida')
    list_filter = ('fecha_reserva', 'atendida')
    list_editable = ('atendida',)
    autocomplete_fields = ('usuario', 'libro')

    def save_model(self, request, obj, form, change):
        # Verificar si ya tiene una reserva activa para ese libro
        reservas_activas = Reserva.objects.filter(
            usuario=obj.usuario,
            libro=obj.libro,
            atendida=False
        )
        if change:
            reservas_activas = reservas_activas.exclude(pk=obj.pk)

        if reservas_activas.exists():
            self.message_user(
                request,
                "❌ Ya existe una reserva activa para este libro por este usuario.",
                level=messages.ERROR
            )
            return

        # Verificar si hay al menos un ejemplar disponible (no prestado o ya devuelto)
        ejemplares = obj.libro.ejemplares.all()
        prestados = Prestamo.objects.filter(
            ejemplar__in=ejemplares,
            devuelto=False
        ).values_list('ejemplar_id', flat=True)

        ejemplares_disponibles = ejemplares.exclude(id__in=prestados)

        if not ejemplares_disponibles.exists():
            self.message_user(
                request,
                "❌ Todos los ejemplares de este libro están actualmente prestados. No se puede reservar.",
                level=messages.ERROR
            )
            return

        # Todo OK, guardar la reserva
        super().save_model(request, obj, form, change)