"""
Modelos de la aplicación usuarios.

Incluye el modelo de Usuario personalizado y el modelo de TokenActivacion
para el sistema de verificación por email e invitación.
"""

import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import timedelta

from .managers import UsuarioManager


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuario personalizado que usa email como identificador principal.

    Hereda de AbstractBaseUser y PermissionsMixin para compatibilidad completa
    con el sistema de autenticación y permisos de Django.
    """

    class Estado(models.TextChoices):
        """Opciones de estado del usuario."""
        PENDIENTE = 'pendiente', 'Pendiente'
        VERIFICADO = 'verificado', 'Verificado'

    class Rol(models.TextChoices):
        """Opciones de rol del usuario."""
        ADMINISTRADOR = 'Administrador', 'Administrador'
        COLABORADOR = 'Colaborador', 'Colaborador'
        CLIENTE = 'Cliente', 'Cliente'

    email = models.EmailField(
        'correo electrónico',
        unique=True,
        help_text='Dirección de email utilizada para iniciar sesión.',
        error_messages={
            'unique': 'Ya existe un usuario con este email.',
        },
    )
    nombre = models.CharField('nombre', max_length=100)
    apellido = models.CharField('apellido', max_length=100)
    estado = models.CharField(
        'estado',
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        help_text='Estado de verificación del usuario.',
    )
    rol = models.CharField(
        'rol',
        max_length=20,
        choices=Rol.choices,
        default=Rol.CLIENTE,
        help_text='Rol del usuario en el sistema.',
    )
    is_active = models.BooleanField(
        'activo',
        default=True,
        help_text='Indica si el usuario puede iniciar sesión.',
    )
    is_staff = models.BooleanField(
        'es staff',
        default=False,
        help_text='Indica si el usuario puede acceder al admin.',
    )
    date_joined = models.DateTimeField(
        'fecha de registro',
        auto_now_add=True,
    )
    empresas = models.ManyToManyField(
        'clientes.Empresa',
        blank=True,
        related_name='usuarios',
        verbose_name='empresas asociadas',
        help_text='Empresas a las que está asociado el usuario.',
    )

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email'], name='idx_usuario_email'),
            models.Index(fields=['estado'], name='idx_usuario_estado'),
            models.Index(fields=['rol'], name='idx_usuario_rol'),
        ]

    def get_full_name(self):
        """Retorna el nombre completo del usuario."""
        return f'{self.nombre} {self.apellido}'.strip()

    def get_short_name(self):
        """Retorna el nombre corto del usuario."""
        return self.nombre

    def __str__(self):
        """Representación en texto del usuario."""
        return self.email


class TokenActivacion(models.Model):
    """
    Token para verificación de email y establecimiento de contraseña.

    Se genera automáticamente al crear un usuario nuevo y tiene una
    validez de 24 horas. También se utiliza para recuperación de contraseña.
    """

    class TipoToken(models.TextChoices):
        """Tipos de token disponibles."""
        ACTIVACION = 'activacion', 'Activación de cuenta'
        RECUPERACION = 'recuperacion', 'Recuperación de contraseña'

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='token_activacion',
        verbose_name='usuario',
    )
    token = models.CharField(
        'token',
        max_length=64,
        unique=True,
        default=uuid.uuid4,
    )
    tipo = models.CharField(
        'tipo',
        max_length=20,
        choices=TipoToken.choices,
        default=TipoToken.ACTIVACION,
    )
    creado_en = models.DateTimeField('creado en', auto_now_add=True)
    expira_en = models.DateTimeField('expira en')

    class Meta:
        verbose_name = 'token de activación'
        verbose_name_plural = 'tokens de activación'

    def save(self, *args, **kwargs):
        """Establecer fecha de expiración si no se ha definido."""
        if not self.expira_en:
            self.expira_en = timezone.now() + timedelta(hours=24)
        if not self.token:
            self.token = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def esta_expirado(self):
        """Verificar si el token ha expirado."""
        return timezone.now() > self.expira_en

    def __str__(self):
        return f'Token de {self.get_tipo_display()} para {self.usuario.email}'
