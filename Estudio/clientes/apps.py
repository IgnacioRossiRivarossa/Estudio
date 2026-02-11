"""Configuración de la aplicación clientes."""

from django.apps import AppConfig


class ClientesConfig(AppConfig):
    """Configuración de la app de clientes."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clientes'
    verbose_name = 'Clientes'
