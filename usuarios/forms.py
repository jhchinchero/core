from django import forms
from django.contrib.auth.forms import AuthenticationForm
from core.models import Usuario
from django.core.exceptions import ValidationError

class RegistroForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['email', 'nombre', 'apellido', 'telefono', 'tipo']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # Hashea la contraseña correctamente
        user.is_staff = False        # No tiene acceso al admin
        user.is_superuser = False    # No es superusuario
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput)
