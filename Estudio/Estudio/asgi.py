"""
Configuración ASGI para el proyecto Estudio.

Expone el callable ASGI como variable de módulo llamada ``application``.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Estudio.settings')

application = get_asgi_application()
