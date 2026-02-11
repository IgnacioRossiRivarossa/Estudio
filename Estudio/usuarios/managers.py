"""
Manager personalizado para el modelo Usuario.

Permite la creación de usuarios y superusuarios usando email
como campo de identificación principal en lugar de username.
"""

from django.contrib.auth.models import BaseUserManager


class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario con email como identificador."""

    def create_user(self, email, nombre, apellido, password=None, **extra_fields):
        """
        Crear y guardar un usuario con el email, nombre, apellido y contraseña dados.

        Args:
            email: Dirección de email del usuario.
            nombre: Nombre del usuario.
            apellido: Apellido del usuario.
            password: Contraseña del usuario (opcional para usuarios por invitación).
            **extra_fields: Campos adicionales.

        Returns:
            Instancia del usuario creado.

        Raises:
            ValueError: Si no se proporciona email.
        """
        if not email:
            raise ValueError('El usuario debe tener una dirección de email.')

        email = self.normalize_email(email)
        usuario = self.model(
            email=email,
            nombre=nombre,
            apellido=apellido,
            **extra_fields,
        )

        if password:
            usuario.set_password(password)
        else:
            # Usuario sin contraseña (se establecerá durante activación)
            usuario.set_unusable_password()

        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, nombre, apellido, password=None, **extra_fields):
        """
        Crear y guardar un superusuario con email, nombre, apellido y contraseña.

        Args:
            email: Dirección de email del superusuario.
            nombre: Nombre del superusuario.
            apellido: Apellido del superusuario.
            password: Contraseña del superusuario.
            **extra_fields: Campos adicionales.

        Returns:
            Instancia del superusuario creado.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('estado', 'verificado')
        extra_fields.setdefault('rol', 'Administrador')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, nombre, apellido, password, **extra_fields)
