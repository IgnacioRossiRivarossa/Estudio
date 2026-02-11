"""
Configuración WSGI para el proyecto Estudio.

Expone el callable WSGI como variable de módulo llamada ``application``.
Usado por Gunicorn en producción (Render).
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Estudio.settings')

application = get_wsgi_application()
