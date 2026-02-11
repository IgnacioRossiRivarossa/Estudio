from django.contrib.auth.models import BaseUserManager


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, apellido, password=None, **extra_fields):
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
