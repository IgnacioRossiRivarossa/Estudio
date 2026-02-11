"""
Formularios de la aplicación usuarios.

Incluye formularios para login, activación de cuenta,
recuperación y cambio de contraseña.
"""

from django import forms
from django.contrib.auth import authenticate, password_validation
from django.core.exceptions import ValidationError

from .models import Usuario


class LoginForm(forms.Form):
    """Formulario de inicio de sesión con email y contraseña."""

    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
            'autofocus': True,
            'autocomplete': 'email',
        }),
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        }),
    )
    recordarme = forms.BooleanField(
        required=False,
        label='Recordarme',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
    )

    def clean(self):
        """Validar credenciales del usuario."""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            # Verificar que el usuario existe
            try:
                usuario = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                raise ValidationError('Email o contraseña incorrectos.')

            # Verificar que el usuario está verificado
            if usuario.estado != 'verificado':
                raise ValidationError(
                    'Tu cuenta aún no ha sido verificada. '
                    'Revisa tu correo electrónico para activarla.'
                )

            # Autenticar usuario
            user = authenticate(username=email, password=password)
            if user is None:
                raise ValidationError('Email o contraseña incorrectos.')

            cleaned_data['user'] = user

        return cleaned_data


class EstablecerPasswordForm(forms.Form):
    """
    Formulario para establecer contraseña inicial (activación de cuenta)
    o nueva contraseña (recuperación).
    """

    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña',
            'autocomplete': 'new-password',
        }),
        help_text=password_validation.password_validators_help_texts(),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña',
            'autocomplete': 'new-password',
        }),
    )

    def clean_password1(self):
        """Validar la contraseña contra las políticas definidas."""
        password1 = self.cleaned_data.get('password1')
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        """Validar que ambas contraseñas coincidan."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden.')

        return cleaned_data


class SolicitarRecuperacionForm(forms.Form):
    """Formulario para solicitar recuperación de contraseña."""

    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
            'autofocus': True,
            'autocomplete': 'email',
        }),
        help_text='Ingresa el email asociado a tu cuenta.',
    )

    def clean_email(self):
        """Validar que el email existe en el sistema."""
        email = self.cleaned_data.get('email')
        # No revelamos si el email existe o no por seguridad,
        # pero guardamos la referencia al usuario si existe
        try:
            self.usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            self.usuario = None
        return email
