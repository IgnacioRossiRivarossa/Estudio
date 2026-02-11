"""Configuración de la aplicación usuarios."""

from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    """Configuración de la app de usuarios."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'
    verbose_name = 'Usuarios'

    def ready(self):
        """Importar señales al iniciar la app."""
        import usuarios.signals  # noqa: F401
